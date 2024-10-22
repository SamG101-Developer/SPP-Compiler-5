from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericArgumentAst import GenericArgumentAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class GenericArgumentGroupAst(Ast, Default):
    tok_left_bracket: TokenAst
    arguments: Seq[GenericArgumentAst]
    tok_right_bracket: TokenAst

    @staticmethod
    def default() -> Default:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
        return GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), Seq(), TokenAst.default(TokenType.TkBrackR))

    def __eq__(self, other: GenericArgumentGroupAst) -> bool:
        return isinstance(other, GenericArgumentGroupAst) and self.arguments == other.arguments


__all__ = ["GenericArgumentGroupAst"]
