from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True)
class IterPatternExhaustedAst(Asts.Ast):
    """
    Represents an iteration pattern that matches an exhausted coroutine, represented by "!!". This is for when any
    generator runs out of values to yield.
    """

    tk_double_exclamation: Asts.TokenAst = field(default=None)
    """The double exclamation token representing the exhausted pattern."""

    def __post_init__(self) -> None:
        """Post-initialization to default the AST nodes."""
        self.tk_double_exclamation = self.tk_double_exclamation or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleExclamationMark)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.tk_double_exclamation.print(printer)

    def __str__(self) -> str:
        return str(self.tk_double_exclamation)

    @property
    def pos_end(self) -> int:
        return self.tk_double_exclamation.pos_end


__all__ = ["IterPatternExhaustedAst"]
