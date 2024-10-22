from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class GenericTypeArgumentUnnamedAst(Ast):
    value: TypeAst

    def __eq__(self, other: GenericTypeArgumentUnnamedAst) -> bool:
        return isinstance(other, GenericTypeArgumentUnnamedAst) and self.value == other.value


__all__ = ["GenericTypeArgumentUnnamedAst"]
