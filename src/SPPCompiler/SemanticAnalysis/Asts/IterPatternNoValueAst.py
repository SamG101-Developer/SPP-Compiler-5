from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True, repr=False)
class IterPatternNoValueAst(Asts.Ast):
    """
    Represents an iteration pattern that matches no value, typically represented by an underscore token. This is for
    when generators are allowed to yield "no-values", for the GenOpt type.
    """

    tk_underscore: Asts.TokenAst = field(default=None)
    """The underscore token representing the no-value pattern."""

    def __post_init__(self) -> None:
        """Post-initialization to default the AST nodes."""
        self.tk_underscore = self.tk_underscore or Asts.TokenAst.raw(self.pos, SppTokenType.TkUnderscore)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.tk_underscore.print(printer)

    def __str__(self) -> str:
        return str(self.tk_underscore)

    @property
    def pos_end(self) -> int:
        return self.tk_underscore.pos_end


__all__ = ["IterPatternNoValueAst"]
