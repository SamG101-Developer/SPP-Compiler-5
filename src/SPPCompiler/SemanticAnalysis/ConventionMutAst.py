from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class ConventionMutAst(Ast, Default):
    tok_borrow: TokenAst
    tok_mut: TokenAst

    @staticmethod
    def default() -> Default:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return ConventionMutAst(-1, TokenAst.default(TokenType.TkBorrow), TokenAst.default(TokenType.KwMut))


__all__ = ["ConventionMutAst"]
