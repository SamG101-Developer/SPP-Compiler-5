from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True, repr=False)
class PatternVariantElseAst(Asts.Ast):
    kw_else: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_else = self.kw_else or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwElse)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.kw_else.print(printer)

    @property
    def pos_end(self) -> int:
        return self.kw_else.pos_end

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Leave this function here (needs the keyword "cond" parameter for uniform pattern analysis).
        ...


__all__ = [
    "PatternVariantElseAst"]
