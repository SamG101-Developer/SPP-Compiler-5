from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class ConventionMutAst(Asts.Ast):
    tok_borrow: Asts.TokenAst = field(default=None)
    tok_mut: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_borrow = self.tok_borrow or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAmpersand)
        self.tok_mut = self.tok_mut or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwMut)

    def __eq__(self, other: ConventionMutAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, ConventionMutAst)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_borrow.print(printer),
            self.tok_mut.print(printer) + " "]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_mut.pos_end


__all__ = [
    "ConventionMutAst"]
