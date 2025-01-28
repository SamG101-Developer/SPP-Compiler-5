from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstBinUtils import AstBinUtils
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class BinaryExpressionAst[T](Ast, TypeInferrable, CompilerStages):
    lhs: Asts.ExpressionAst = field(default=None)
    op: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkAdd))
    rhs: Asts.ExpressionAst = field(default=None)

    _as_func: Optional[Asts.PostfixExpressionAst | Asts.CaseExpressionAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        assert self.lhs and self.rhs

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer) + " ",
            self.op.print(printer) + " ",
            self.rhs.print(printer)]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType

        # Comparisons using the "is" keyword are always boolean.
        if self.op.token.token_type == SppTokenType.KwIs:
            bool_type = CommonTypes.Bool(self.pos)
            return InferredType.from_type(bool_type)

        # Infer the type from the function equivalent of the binary expression.
        if not self._as_func:
            self.analyse_semantics(scope_manager, **kwargs)
        return self._as_func.infer_type(scope_manager, **kwargs)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The TypeAst cannot be used as an expression for a binary operation.
        if isinstance(self.lhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.lhs)
        if isinstance(self.rhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.rhs)

        # Analyse the LHS of the binary expression.
        self.lhs.analyse_semantics(scope_manager, **kwargs)
        AstMemoryHandler.enforce_memory_integrity(self.lhs, self.op, scope_manager, update_memory_info=False)

        # If the RHS is a destructure, then analysis stops here (after analysing the conversion).
        if self.op.token.token_type == SppTokenType.KwIs:
            n = scope_manager.current_scope.children.length
            self._as_func = AstBinUtils.convert_to_function_call(self)
            self._as_func.analyse_semantics(scope_manager, **kwargs)
            destructures_symbols = scope_manager.current_scope.children[n].children[0].all_symbols(exclusive=True)
            for symbol in destructures_symbols:
                scope_manager.current_scope.add_symbol(symbol)
            return

        # Ensure the memory status of the left and right hand side.
        self.rhs.analyse_semantics(scope_manager, **kwargs)
        if not isinstance(self.rhs, Asts.TokenAst) and not isinstance(self.lhs, Asts.TokenAst):
            AstMemoryHandler.enforce_memory_integrity(self.rhs, self.op, scope_manager)

        # Check for compound assignment (for example "+="), that the lhs is symbolic.
        if self.op.token.token_type.name.endswith("Assign") and not scope_manager.current_scope.get_variable_symbol_outermost_part(self.lhs):
            raise SemanticErrors.AssignmentInvalidCompoundLhsError().add(self.lhs)

        # Todo: Check on the tuple size to be > 1 ?
        # Handle lhs-folding
        if isinstance(self.lhs, Asts.TokenAst):
            # Check the rhs is a tuple.
            rhs_tuple_type = self.rhs.infer_type(scope_manager, **kwargs).type
            if not rhs_tuple_type.without_generics().symbolic_eq(CommonTypes.Tup(), scope_manager.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(self.rhs, rhs_tuple_type, self.lhs)

            rhs_num_elements = rhs_tuple_type.types[-1].generic_argument_group.arguments.length

            # Get the parts of the tuple.
            new_asts = Seq()
            for i in range(rhs_num_elements):
                new_ast = AstMutation.inject_code(f"{self.rhs}.{i}", SppParser.parse_postfix_expression)
                new_ast.analyse_semantics(scope_manager, **kwargs)
                new_asts.append(new_ast)

            # Convert "t = (0, 1, 2, 3)", ".. + t" into "(((t.0 + t.1) + t.2) + t.3)".
            self.lhs, self.rhs = new_asts[0], new_asts[1]
            for new_ast in new_asts[2:]:
                self.lhs, self.rhs = BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs), new_ast
            self._as_func = AstBinUtils.convert_to_function_call(self)
            self._as_func.analyse_semantics(scope_manager, **kwargs)

        # Handle rhs-folding
        elif isinstance(self.rhs, Asts.TokenAst):
            # Check the rhs is a tuple.
            lhs_tuple_type = self.lhs.infer_type(scope_manager, **kwargs).type
            if not lhs_tuple_type.without_generics().symbolic_eq(CommonTypes.Tup(), scope_manager.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(self.rhs, lhs_tuple_type, self.lhs)

            lhs_num_elements = lhs_tuple_type.types[-1].generic_argument_group.arguments.length

            # Get the parts of the tuple.
            new_asts = Seq()
            for i in range(lhs_num_elements):
                new_ast = AstMutation.inject_code(f"{self.lhs}.{i}", SppParser.parse_postfix_expression)
                new_ast.analyse_semantics(scope_manager, **kwargs)
                new_asts.append(new_ast)

            # Convert "t = (0, 1, 2, 3)", "t + .." into "(t.0 + (t.1 + (t.2 + t.3)))".
            self.lhs, self.rhs = new_asts[-2], new_asts[-1]
            for new_ast in new_asts[:-2].reverse():
                self.lhs, self.rhs = new_ast, BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs)
            self._as_func = AstBinUtils.convert_to_function_call(self)
            self._as_func.analyse_semantics(scope_manager, **kwargs)

        # Analyse the function equivalent of the binary expression.
        else:
            self._as_func = AstBinUtils.convert_to_function_call(self)
            self._as_func.analyse_semantics(scope_manager, **kwargs)


__all__ = ["BinaryExpressionAst"]
