from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class ConventionRefAst(Ast, Default):
    tok_borrow: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_borrow.print(printer)

    @staticmethod
    def default() -> ConventionRefAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return ConventionRefAst(-1, TokenAst.default(TokenType.TkBorrow))


__all__ = ["ConventionRefAst"]
