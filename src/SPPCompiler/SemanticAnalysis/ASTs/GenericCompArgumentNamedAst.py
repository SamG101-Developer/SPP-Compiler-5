from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst


@dataclass
class GenericCompArgumentNamedAst(Ast):
    name: TypeAst
    tok_assign: TokenAst
    value: ExpressionAst

    def __post_init__(self):
        from SPPCompiler.SemanticAnalysis import TypeAst
        self.name = TypeAst.from_identifier(self.name)

    def __eq__(self, other: GenericCompArgumentNamedAst) -> bool:
        return isinstance(other, GenericCompArgumentNamedAst) and self.name == other.name and self.value == other.value


__all__ = ["GenericCompArgumentNamedAst"]
