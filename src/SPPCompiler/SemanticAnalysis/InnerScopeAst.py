from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class InnerScopeAst[T](Ast, Default):
    tok_left_brace: TokenAst
    members: Seq[T]
    tok_right_brace: TokenAst

    def __post_init__(self) -> None:
        self.members = Seq(self.members)

    @staticmethod
    def default(body: Seq[T] = None) -> InnerScopeAst[T]:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
        return InnerScopeAst(-1, TokenAst.default(TokenType.TkBraceL), body or Seq(), TokenAst.default(TokenType.TkBraceR))
