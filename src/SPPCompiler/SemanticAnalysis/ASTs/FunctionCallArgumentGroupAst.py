from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentAst import FunctionCallArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentNamedAst import FunctionCallArgumentNamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentUnnamedAst import FunctionCallArgumentUnnamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class FunctionCallArgumentGroupAst(Ast, Default):
    tok_left_paren: TokenAst
    arguments: Seq[FunctionCallArgumentAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the arguments into a sequence.
        self.arguments = Seq(self.arguments)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.arguments.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @staticmethod
    def default(arguments: Seq[FunctionCallArgumentAst] = None) -> FunctionCallArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return FunctionCallArgumentGroupAst(-1, TokenAst.default(TokenType.TkParenL), arguments or Seq(), TokenAst.default(TokenType.TkParenR))

    def get_named(self) -> Seq[FunctionCallArgumentNamedAst]:
        # Get all the named function call arguments.
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentNamedAst
        return self.arguments.filter_to_type(FunctionCallArgumentNamedAst)

    def get_unnamed(self) -> Seq[FunctionCallArgumentUnnamedAst]:
        # Get all the unnamed function call arguments.
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentUnnamedAst
        return self.arguments.filter_to_type(FunctionCallArgumentUnnamedAst)

    def __eq__(self, other: FunctionCallArgumentGroupAst) -> bool:
        return isinstance(other, FunctionCallArgumentGroupAst) and self.arguments == other.arguments


__all__ = ["FunctionCallArgumentGroupAst"]
