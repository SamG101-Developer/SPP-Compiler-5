from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class PatternVariantElseCaseAst(Asts.Ast):
    tok_else: Asts.TokenAst = field(default=None)
    case_expression: Asts.CaseExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_else = self.tok_else or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwElse)
        assert self.case_expression is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_else.print(printer) + " ",
            self.case_expression.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.case_expression.pos_end

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Analyse the case expression.
        self.case_expression.analyse_semantics(sm, **kwargs)


__all__ = [
    "PatternVariantElseCaseAst"]
