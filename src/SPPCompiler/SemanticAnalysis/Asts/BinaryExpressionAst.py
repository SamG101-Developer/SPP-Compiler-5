from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstBinUtils import AstBinUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class BinaryExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """!
    The BinaryExpressionAst class is an AST node that represents a binary expression. This AST can be used to represent
    any binary operation, such as addition, subtraction, multiplication, division, etc. The binary expression is
    represented as "lhs op rhs", where "lhs" and "rhs" are the left and right hand side expressions, and "op" is the
    operator.

    Example:
        x + 10

    The above example would be represented as a BinaryExpressionAst with the "+" operator, and the left hand side being
    the variable "x", and the right hand side being the integer literal "10". Binary expressions are converted into
    functions for analysis, such as "x.add(10)".
    """

    lhs: Asts.ExpressionAst = field(default=None)
    op: Asts.TokenAst = field(default=None)
    rhs: Asts.ExpressionAst = field(default=None)

    _as_func: Optional[Asts.PostfixExpressionAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.op = self.op or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.NoToken)
        assert self.lhs is not None and self.rhs is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer) + " ",
            self.op.print(printer) + " ",
            self.rhs.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.rhs.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """!
        The inferred type is always the return type of the converted function equivalent. As this is not fixed
        (operations have generic return types), the function equivalent is analysed to determine the return type.
        @param sm The scope manager.
        @param kwargs Additional keyword arguments.
        @return The inferred type of the binary expression.
        """

        # Comparisons using the "is" keyword are always boolean.
        if self.op.token_type == SppTokenType.KwIs:
            return CommonTypes.Bool(self.pos)

        # Infer the type from the function equivalent of the binary expression.
        if not self._as_func:
            self.analyse_semantics(sm, **kwargs)
        return self._as_func.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """!
        Most of the analysis for binary expressions is offloaded into the function equivalent of the binary expression
        (memory checks, type checks, etc). Some memory checks are done beforehand to short-circuit the analysis. Other
        checks include the assignment operations (+=, -= etc) requiring the LHS to be symbolic, and binary folding.
        @param sm The scope manager.
        @param kwargs Additional keyword arguments.
        @throw ExpressionTypeInvalidError If the LHS or RHS is an invalid expression.
        @throw AssignmentInvalidCompoundLhsError If the LHS is not symbolic for a compound assignment.
        @throw MemberAccessNonIndexableError If the LHS or RHS is not indexable for a fold operation.
        """

        # The TypeAst cannot be used as an expression for a binary operation.
        if isinstance(self.lhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.lhs).scopes(sm.current_scope)
        if isinstance(self.rhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.rhs).scopes(sm.current_scope)

        # Analyse the LHS of the binary expression.
        self.lhs.analyse_semantics(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(self.lhs, self.op, sm, update_memory_info=False, check_move_from_borrowed_context=False)

        # Ensure the memory status of the left and right hand side.
        self.rhs.analyse_semantics(sm, **kwargs)
        if not isinstance(self.rhs, Asts.TokenAst) and not isinstance(self.lhs, Asts.TokenAst):
            AstMemoryUtils.enforce_memory_integrity(self.rhs, self.op, sm)

        # Check for compound assignment (for example "+="), that the lhs is symbolic.
        if self.op.token_type.name.endswith("Assign") and not sm.current_scope.get_variable_symbol_outermost_part(self.lhs):
            raise SemanticErrors.AssignmentInvalidCompoundLhsError().add(self.lhs).scopes(sm.current_scope)

        # Todo: Check on the tuple size to be > 1 ?
        # Handle lhs-folding
        if isinstance(self.lhs, Asts.TokenAst):
            # Check the rhs is a tuple.
            rhs_tuple_type = self.rhs.infer_type(sm, **kwargs)
            if not rhs_tuple_type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, sm.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(
                    self.rhs, rhs_tuple_type, self.lhs).scopes(sm.current_scope)

            rhs_num_elements = rhs_tuple_type.type_parts()[0].generic_argument_group.arguments.length

            # Get the parts of the tuple.
            new_asts = Seq()
            for i in range(rhs_num_elements):
                new_ast = CodeInjection.inject_code(f"{self.rhs}.{i}", SppParser.parse_postfix_expression, pos_adjust=self.rhs.pos)
                new_ast.analyse_semantics(sm, **kwargs)
                new_asts.append(new_ast)

            # Convert "t = (0, 1, 2, 3)", ".. + t" into "(((t.0 + t.1) + t.2) + t.3)".
            self.lhs, self.rhs = new_asts[0], new_asts[1]
            for new_ast in new_asts[2:]:
                self.lhs, self.rhs = BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs), new_ast
            self._as_func = AstBinUtils.convert_to_function_call(self)
            self._as_func.analyse_semantics(sm, **kwargs)

        # Handle rhs-folding
        elif isinstance(self.rhs, Asts.TokenAst):
            # Check the rhs is a tuple.
            lhs_tuple_type = self.lhs.infer_type(sm, **kwargs)
            if not lhs_tuple_type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, sm.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(
                    self.rhs, lhs_tuple_type, self.lhs).scopes(sm.current_scope)

            lhs_num_elements = lhs_tuple_type.type_parts()[0].generic_argument_group.arguments.length

            # Get the parts of the tuple.
            new_asts = Seq()
            for i in range(lhs_num_elements):
                new_ast = CodeInjection.inject_code(f"{self.lhs}.{i}", SppParser.parse_postfix_expression, pos_adjust=self.lhs.pos)
                new_ast.analyse_semantics(sm, **kwargs)
                new_asts.append(new_ast)

            # Convert "t = (0, 1, 2, 3)", "t + .." into "(t.0 + (t.1 + (t.2 + t.3)))".
            self.lhs, self.rhs = new_asts[-2], new_asts[-1]
            for new_ast in new_asts[:-2].reverse():
                self.lhs, self.rhs = new_ast, BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs)
            self._as_func = AstBinUtils.convert_to_function_call(self)
            self._as_func.analyse_semantics(sm, **kwargs)

        # Analyse the function equivalent of the binary expression.
        else:
            self._as_func = AstBinUtils.convert_to_function_call(self)
            self._as_func.analyse_semantics(sm, **kwargs)


__all__ = [
    "BinaryExpressionAst"]
