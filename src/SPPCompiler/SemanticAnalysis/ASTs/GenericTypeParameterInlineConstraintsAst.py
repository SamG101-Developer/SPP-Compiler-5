from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class GenericTypeParameterInlineConstraintsAst(Ast, Default):
    tok_colon: TokenAst
    constraints: Seq[TypeAst]

    def __post_init__(self) -> None:
        self.constraints = Seq(self.constraints)

    @staticmethod
    def default() -> GenericTypeParameterInlineConstraintsAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return GenericTypeParameterInlineConstraintsAst(-1, TokenAst.default(TokenType.TkColon), Seq())


__all__ = ["GenericTypeParameterInlineConstraintsAst"]
