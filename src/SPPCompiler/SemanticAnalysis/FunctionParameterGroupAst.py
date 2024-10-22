from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.FunctionParameterAst import FunctionParameterAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class FunctionParameterGroupAst(Ast, Default):
    tok_left_paren: TokenAst
    parameters: Seq[FunctionParameterAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.parameters = Seq(self.parameters)

    @staticmethod
    def default() -> Default:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
        return FunctionParameterGroupAst(-1, TokenAst.default(TokenType.TkParenL), Seq(), TokenAst.default(TokenType.TkParenR))

    def __eq__(self, other: FunctionParameterGroupAst) -> bool:
        return isinstance(other, FunctionParameterGroupAst) and self.parameters == other.parameters


__all__ = ["FunctionParameterGroupAst"]
