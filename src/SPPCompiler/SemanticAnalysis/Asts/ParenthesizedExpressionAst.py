from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class ParenthesizedExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_l: Asts.TokenAst = field(default=None)
    expr: Asts.ExpressionAst = field(default=None)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)
        assert self.expr is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            self.expr.print(printer),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type of the expression.
        return self.expr.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expr, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.expr).scopes(sm.current_scope)

        # Analyse the expression.
        self.expr.analyse_semantics(sm, **kwargs)


__all__ = [
    "ParenthesizedExpressionAst"]
