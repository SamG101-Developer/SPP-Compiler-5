from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class BooleanLiteralAst(Ast):
    value: TokenAst

    def __eq__(self, other: BooleanLiteralAst) -> bool:
        return self.value == other.value


__all__ = ["BooleanLiteralAst"]
