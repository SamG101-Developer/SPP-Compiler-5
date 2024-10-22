from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class FunctionCallArgumentUnnamedAst(Ast):
    convention: ConventionAst
    tok_unpack: Optional[TokenAst]
    value: ExpressionAst

    def __eq__(self, other: FunctionCallArgumentUnnamedAst) -> bool:
        return isinstance(other, FunctionCallArgumentUnnamedAst) and self.value == other.value


__all__ = ["FunctionCallArgumentUnnamedAst"]
