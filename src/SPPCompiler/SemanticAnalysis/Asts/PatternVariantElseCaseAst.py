from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True)
class PatternVariantElseCaseAst(Asts.Ast):
    kw_else: Asts.TokenAst = field(default=None)
    case_expression: Asts.CaseExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_else = self.kw_else or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwElse)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_else.print(printer) + " ",
            self.case_expression.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.case_expression.pos_end

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Analyse the case expression.
        self.case_expression.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self.case_expression.check_memory(sm, **kwargs)


__all__ = [
    "PatternVariantElseCaseAst"]
