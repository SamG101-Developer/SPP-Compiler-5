from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class ConventionMutAst(Ast, Default):
    tok_borrow: TokenAst
    tok_mut: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_borrow.print(printer),
            self.tok_mut.print(printer) + " "]
        return "".join(string)

    @staticmethod
    def default() -> ConventionMutAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return ConventionMutAst(-1, TokenAst.default(TokenType.TkBorrow), TokenAst.default(TokenType.KwMut))


__all__ = ["ConventionMutAst"]
