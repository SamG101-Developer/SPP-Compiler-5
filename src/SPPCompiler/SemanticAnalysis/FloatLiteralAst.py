from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class FloatLiteralAst(Ast):
    tok_sign: Optional[TokenAst]
    value: TokenAst
    type: Optional[TypeAst]

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
        self.type = TypeAst.from_identifier(self.type)

    def __eq__(self, other: FloatLiteralAst) -> bool:
        return isinstance(other, FloatLiteralAst) and self.tok_sign == other.tok_sign and int(self.value.token.token_metadata) == int(other.value.token.token_metadata)


__all__ = ["FloatLiteralAst"]
