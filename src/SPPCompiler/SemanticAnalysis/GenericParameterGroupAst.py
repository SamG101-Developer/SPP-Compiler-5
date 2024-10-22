from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericParameterAst import GenericParameterAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class GenericParameterGroupAst(Ast, Default):
    tok_left_bracket: TokenAst
    parameters: Seq[GenericParameterAst]
    tok_right_bracket: TokenAst

    def __post_init__(self) -> None:
        self.parameters = Seq(self.parameters)

    @staticmethod
    def default() -> Default:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TokenAst
        return GenericParameterGroupAst(-1, TokenAst.default(TokenType.TkBrackL), Seq(), TokenAst.default(TokenType.TkBrackR))


__all__ = ["GenericParameterGroupAst"]
