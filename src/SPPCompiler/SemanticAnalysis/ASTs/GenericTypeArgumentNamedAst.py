from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class GenericTypeArgumentNamedAst(Ast):
    name: TypeAst
    tok_assign: TokenAst
    value: TypeAst

    def __eq__(self, other: GenericTypeArgumentNamedAst) -> bool:
        return isinstance(other, GenericTypeArgumentNamedAst) and self.name == other.name and self.value == other.value


__all__ = ["GenericTypeArgumentNamedAst"]
