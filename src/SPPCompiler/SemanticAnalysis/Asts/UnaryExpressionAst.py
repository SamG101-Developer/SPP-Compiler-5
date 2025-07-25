from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class UnaryExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    op: Asts.UnaryExpressionOperatorAst = field(default=None)
    rhs: Asts.ExpressionAst = field(default=None)

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.op.print(printer),
            self.rhs.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.rhs.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type of the unary operation being applied to the "rhs".
        return self.op.infer_type(sm, rhs=self.rhs, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the rhs.
        if isinstance(self.rhs, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.rhs).scopes(sm.current_scope)

        # Analyse the "op" and the "rhs".
        self.rhs.analyse_semantics(sm, **kwargs)
        self.op.analyse_semantics(sm, rhs=self.rhs, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self.rhs.check_memory(sm, **kwargs)


__all__ = [
    "UnaryExpressionAst"]
