from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst


@dataclass
class GenericCompArgumentUnnamedAst(Ast):
    value: ExpressionAst

    def __eq__(self, other: GenericCompArgumentUnnamedAst) -> bool:
        return isinstance(other, GenericCompArgumentUnnamedAst) and self.value == other.value


__all__ = ["GenericCompArgumentUnnamedAst"]
