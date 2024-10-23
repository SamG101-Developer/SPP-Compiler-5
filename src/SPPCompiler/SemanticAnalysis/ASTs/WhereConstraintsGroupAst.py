from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereConstraintsAst import WhereConstraintsAst


@dataclass
class WhereConstraintsGroupAst(Ast, Default):
    tok_left_brack: TokenAst
    constraints: Seq[WhereConstraintsAst]
    tok_right_brack: TokenAst

    def __post_init__(self) -> None:
        self.constraints = Seq(self.constraints)

    @staticmethod
    def default() -> WhereConstraintsGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return WhereConstraintsGroupAst(-1, TokenAst.default(TokenType.TkBrackL), Seq(), TokenAst.default(TokenType.TkBrackR))


__all__ = ["WhereConstraintsGroupAst"]
