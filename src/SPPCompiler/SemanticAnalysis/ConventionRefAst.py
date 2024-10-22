from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class ConventionRefAst(Ast, Default):
    tok_borrow: TokenAst

    @staticmethod
    def default() -> Default:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return ConventionRefAst(-1, TokenAst.default(tok=TokenType.TkBorrow))


__all__ = ["ConventionRefAst"]
