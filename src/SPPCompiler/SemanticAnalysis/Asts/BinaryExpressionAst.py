from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstBinUtils import AstBinUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


@dataclass(slots=True)
class BinaryExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The BinaryExpressionAst class is an AST node that represents a binary expression. This AST can be used to represent
    any binary operation, such as addition, subtraction, multiplication, division, etc. The binary expression is
    represented as "lhs op rhs", where "lhs" and "rhs" are the left and right hand side expressions, and "op" is the
    operator.

    Example:

    .. code-block:: S++

        x + 10

    The above example would be represented as a BinaryExpressionAst with the "+" operator, and the left hand side being
    the variable "x", and the right hand side being the integer literal "10". Binary expressions are converted into
    functions for analysis, such as "x.add(10)".
    """

    lhs: Asts.ExpressionAst = field(default=None)
    """The lhs operands of the binary expression."""

    op: Asts.TokenAst = field(default=None)
    """The operator of the binary expression."""

    rhs: Asts.ExpressionAst = field(default=None)
    """The rhs operands of the binary expression."""

    _as_func: Optional[Asts.PostfixExpressionAst] = field(default=None, init=False, repr=False)
    """The function representation of the binary expression."""

    def __post_init__(self) -> None:
        self.op = self.op or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.NoToken)

    def __hash__(self) -> int:
        return id(self)

    def __str__(self) -> str:
        # Add () for debugging.
        return f"({self.lhs} {self.op} {self.rhs})"

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
        """
        The inferred type of a binary expression is the return type of the equivalent method call. This is not a fixed
        type, as operation classes have a generic "Ret" type. The expression ``1 + 2`` becomes ``1.add(2)``, which is
        inferred as ``BigInt::add(1, 2)``, and the return type is ``BigInt``. This also handles multiple overloads, as
        the entire postfix function call is analysed for its respective return type.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The type of the result of executing the binary expression.
        """

        # Infer the type from the function equivalent of the binary expression.
        if not self._as_func:
            self.analyse_semantics(sm, **kwargs)
        return self._as_func.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        Most of the analysis of a binary expression is offloaded into the postfix function call, including type checks,
        memory checks etc. Some memory checks are done beforehand, to short-circuit execution.

        The checks unique to the binary expression include the compound assignment operations requiring a symbolic LHS,
        and binary folding operations.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: None.
        :raise SemanticErrors.AssignmentInvalidCompoundLhsError: This exception is raised when the left-hand side of a
            compound assignment is non-symbolic. For example "1 += 2" is invalid.
        :raise SemanticErrors.MemberAccessNonIndexableError: This exception is raised when trying to binary-fold a
            non-indexable type.
        """

        # The TypeAst cannot be used as an expression for a binary operation.
        if isinstance(self.lhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.lhs).scopes(sm.current_scope)
        if isinstance(self.rhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.rhs).scopes(sm.current_scope)

        # Analyse the parts of the binary expression.
        self.rhs.analyse_semantics(sm, **kwargs)
        self.lhs.analyse_semantics(sm, **kwargs)
        if not isinstance(self.lhs, Asts.TokenAst):
            AstMemoryUtils.enforce_memory_integrity(self.rhs, self.op, sm)
        AstMemoryUtils.enforce_memory_integrity(self.lhs, self.op, sm, update_memory_info=False, check_move_from_borrowed_context=False)

        # Check for compound assignment (for example "+="), that the lhs is symbolic.
        if self.op.token_type.name.endswith("Assign") and not sm.current_scope.get_variable_symbol_outermost_part(self.lhs):
            raise SemanticErrors.AssignmentInvalidCompoundLhsError().add(self.lhs).scopes(sm.current_scope)

        # Todo: Check on the tuple size to be > 1 ?
        # Todo: Instead of tuple checks, do the "indexable" check - allow folding arrays too?
        # Handle lhs-folding
        if isinstance(self.lhs, Asts.TokenAst):
            # Check the rhs is a tuple.
            rhs_tuple_type = self.rhs.infer_type(sm, **kwargs)
            if not AstTypeUtils.is_type_tuple(rhs_tuple_type, sm.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(
                    self.rhs, rhs_tuple_type, self.lhs).scopes(sm.current_scope)

            rhs_num_elements = len(rhs_tuple_type.type_parts()[0].generic_argument_group.arguments)

            # Get the parts of the tuple.
            new_asts = []
            for i in range(rhs_num_elements):
                new_ast = CodeInjection.inject_code(f"{self.rhs}.{i}", SppParser.parse_postfix_expression, pos_adjust=self.rhs.pos)
                new_ast.analyse_semantics(sm, **kwargs)
                new_asts.append(new_ast)

            # Convert "t = (0, 1, 2, 3)", ".. + t" into "(((t.0 + t.1) + t.2) + t.3)".
            self.lhs, self.rhs = new_asts[0], new_asts[1]
            for new_ast in new_asts[2:]:
                self.lhs, self.rhs = BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs), new_ast
            self._as_func = AstBinUtils.convert_to_function_call(self, sm)
            self._as_func.analyse_semantics(sm, **kwargs)

        # Handle rhs-folding
        elif isinstance(self.rhs, Asts.TokenAst):
            # Check the rhs is a tuple.
            lhs_tuple_type = self.lhs.infer_type(sm, **kwargs)
            if not AstTypeUtils.is_type_tuple(lhs_tuple_type, sm.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(
                    self.rhs, lhs_tuple_type, self.lhs).scopes(sm.current_scope)

            lhs_num_elements = len(lhs_tuple_type.type_parts()[0].generic_argument_group.arguments)

            # Get the parts of the tuple.
            new_asts = []
            for i in range(lhs_num_elements):
                new_ast = CodeInjection.inject_code(f"{self.lhs}.{i}", SppParser.parse_postfix_expression, pos_adjust=self.lhs.pos)
                new_ast.analyse_semantics(sm, **kwargs)
                new_asts.append(new_ast)

            # Convert "t = (0, 1, 2, 3)", "t + .." into "(t.0 + (t.1 + (t.2 + t.3)))".
            self.lhs, self.rhs = new_asts[-2], new_asts[-1]
            for new_ast in reversed(new_asts[:-2]):
                self.lhs, self.rhs = new_ast, BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs)
            self._as_func = AstBinUtils.convert_to_function_call(self, sm)
            self._as_func.analyse_semantics(sm, **kwargs)

        # Analyse the function equivalent of the binary expression.
        else:
            self._as_func = AstBinUtils.convert_to_function_call(self, sm)
            self._as_func.analyse_semantics(sm, **kwargs)


__all__ = [
    "BinaryExpressionAst"]
