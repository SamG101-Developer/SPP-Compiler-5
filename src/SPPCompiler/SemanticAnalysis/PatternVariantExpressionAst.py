from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst


@dataclass
class PatternVariantExpressionAst(Ast):
    expression: ExpressionAst


__all__ = ["PatternVariantExpressionAst"]
