from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True)
class ConventionRefAst(Asts.Ast):
    tok_borrow: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_borrow = self.tok_borrow or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAmpersand)

    def __eq__(self, other: ConventionRefAst) -> bool:
        # Check both ASTs are the same type.
        return type(other) is ConventionRefAst

    def __hash__(self) -> int:
        # Hash the AST.
        return 2

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_borrow.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_borrow.pos_end


__all__ = [
    "ConventionRefAst"]
