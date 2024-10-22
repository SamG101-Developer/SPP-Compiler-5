from __future__ import annotations
from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast


@dataclass
class BooleanLiteralAst(Ast):
    value: bool

    def __eq__(self, other: BooleanLiteralAst) -> bool:
        return self.value == other.value


__all__ = ["BooleanLiteralAst"]
