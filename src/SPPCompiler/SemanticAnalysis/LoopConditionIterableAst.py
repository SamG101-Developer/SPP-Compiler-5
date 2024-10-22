from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class LoopConditionIterableAst(Ast):
    variable: LocalVariableAst
    in_keyword: TokenAst
    iterable: ExpressionAst


__all__ = ["LoopConditionIterableAst"]
