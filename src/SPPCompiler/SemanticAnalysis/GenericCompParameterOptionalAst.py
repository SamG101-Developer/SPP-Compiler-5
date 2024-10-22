from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst


@dataclass
class GenericCompParameterOptionalAst(Ast):
    tok_cmp: TokenAst
    name: IdentifierAst
    tok_colon: TokenAst
    type: TypeAst
    tok_assign: TokenAst
    default: ExpressionAst

    def __post_init__(self):
        from SPPCompiler.SemanticAnalysis import TypeAst
        self.name = TypeAst.from_identifier(self.name)


__all__ = ["GenericCompParameterOptionalAst"]
