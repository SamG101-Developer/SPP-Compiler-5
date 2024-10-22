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

    @staticmethod
    def default() -> Default:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
        return InnerScopeAst(-1, TokenAst.dummy(TokenType.TkBraceL), Seq(), TokenAst.dummy(TokenType.TkBraceR))
