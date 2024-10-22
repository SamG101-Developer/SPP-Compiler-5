from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst


@dataclass
class LoopConditionBooleanAst(Ast):
    condition: ExpressionAst


__all__ = ["LoopConditionBooleanAst"]
