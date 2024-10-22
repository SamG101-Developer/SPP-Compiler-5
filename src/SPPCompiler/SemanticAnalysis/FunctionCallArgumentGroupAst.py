from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.FunctionCallArgumentAst import FunctionCallArgumentAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class FunctionCallArgumentGroupAst(Ast, Default):
    tok_left_paren: TokenAst
    arguments: Seq[FunctionCallArgumentAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.arguments = Seq(self.arguments)

    @staticmethod
    def default() -> Default:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
        return FunctionCallArgumentGroupAst(-1, TokenAst.default(TokenType.TkParenL), Seq(), TokenAst.default(TokenType.TkParenR))

    def __eq__(self, other: FunctionCallArgumentGroupAst) -> bool:
        return isinstance(other, FunctionCallArgumentGroupAst) and self.arguments == other.arguments


__all__ = ["FunctionCallArgumentGroupAst"]
