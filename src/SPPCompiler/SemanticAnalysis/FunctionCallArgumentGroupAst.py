from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.FunctionCallArgumentAst import FunctionCallArgumentAst
    from SPPCompiler.SemanticAnalysis.FunctionCallArgumentNamedAst import FunctionCallArgumentNamedAst
    from SPPCompiler.SemanticAnalysis.FunctionCallArgumentUnnamedAst import FunctionCallArgumentUnnamedAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class FunctionCallArgumentGroupAst(Ast, Default):
    tok_left_paren: TokenAst
    arguments: Seq[FunctionCallArgumentAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.arguments = Seq(self.arguments)

    @staticmethod
    def default(arguments: Seq[FunctionCallArgumentAst] = None) -> FunctionCallArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
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
