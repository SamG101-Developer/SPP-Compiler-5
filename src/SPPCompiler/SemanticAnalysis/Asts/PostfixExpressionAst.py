from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class PostfixExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    lhs: Asts.ExpressionAst = field(default=None)
    op: Asts.PostfixExpressionOperatorAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.lhs is not None and self.op is not None

    def __eq__(self, other: PostfixExpressionAst) -> bool:
        return isinstance(other, PostfixExpressionAst) and self.lhs == other.lhs and self.op == other.op

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer),
            self.op.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.op.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type of the postfix operation being applied to the "lhs".
        return self.op.infer_type(sm, lhs=self.lhs, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst cannot be used as an expression for the lhs.
        if isinstance(self.lhs, Asts.TokenAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.lhs).scopes(sm.current_scope)

        # Analyse the "lhs" and "op".
        self.lhs.analyse_semantics(sm, **kwargs)
        self.op.analyse_semantics(sm, lhs=self.lhs, **kwargs)


__all__ = [
    "PostfixExpressionAst"]
