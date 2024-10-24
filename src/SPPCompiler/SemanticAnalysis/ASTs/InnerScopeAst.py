from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class InnerScopeAst[T](Ast, Default):
    tok_left_brace: TokenAst
    members: Seq[T]
    tok_right_brace: TokenAst

    def __post_init__(self) -> None:
        # Convert the members into a sequence.
        self.members = Seq(self.members)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.members:
            string = [
                self.tok_left_brace.print(printer) + "\n",
                self.members.print(printer, "\n"),
                self.tok_right_brace.print(printer) + "\n"]
        else:
            string = [
                self.tok_left_brace.print(printer),
                self.tok_right_brace.print(printer) + "\n"]
        return "".join(string)

    @staticmethod
    def default(body: Seq[T] = None) -> InnerScopeAst[T]:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return InnerScopeAst(-1, TokenAst.default(TokenType.TkBraceL), body or Seq(), TokenAst.default(TokenType.TkBraceR))
