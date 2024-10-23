from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereConstraintsGroupAst import WhereConstraintsGroupAst


@dataclass
class WhereBlockAst(Ast, Default):
    tok_where: TokenAst
    constraint_group: WhereConstraintsGroupAst

    @staticmethod
    def default() -> WhereBlockAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import WhereConstraintsGroupAst, TokenAst
        return WhereBlockAst(-1, TokenAst.default(TokenType.KwWhere), WhereConstraintsGroupAst.default())


__all__ = ["WhereBlockAst"]