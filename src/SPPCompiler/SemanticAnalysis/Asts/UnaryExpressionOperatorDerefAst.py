from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class UnaryExpressionOperatorDerefAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The dereference operator can be used in a very specific context - to when the RHS is a borrow type that superimposes
    the Copy type. The operator then copies the value inside the borrow, and returns it as a value.
    """

    tok_deref: Asts.TokenAst = field(default=None)

    def __str__(self) -> str:
        return str(self.tok_deref)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.tok_deref.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_deref.pos_end

    def infer_type(self, sm: ScopeManager, rhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Get the RHS type, and remove the borrow convention.
        rhs_type = rhs.infer_type(sm, **kwargs).without_convention
        return rhs_type

    def analyse_semantics(self, sm: ScopeManager, rhs: Asts.ExpressionAst = None, **kwargs) -> None:
        rhs_type = rhs.infer_type(sm, **kwargs)

        # Check the RHS is a borrow type.
        if rhs_type.convention is None:
            raise SemanticErrors.InvalidDereferenceExpressionConvention().add(
                self, rhs, rhs_type).scopes(sm.current_scope)

        # Check the RHS is a Copy type.
        if not sm.current_scope.get_symbol(rhs_type).is_copyable():
            raise SemanticErrors.InvalidDereferenceExpressionType().add(
                self, rhs, rhs_type.without_convention).scopes(sm.current_scope)


__all__ = [
    "UnaryExpressionOperatorDerefAst"
]
