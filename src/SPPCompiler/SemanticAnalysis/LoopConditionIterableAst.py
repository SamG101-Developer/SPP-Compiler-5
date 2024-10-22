from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst


@dataclass
class LoopConditionIterableAst(Ast):
    variable: LocalVariableAst
    in_keyword: TokenAst
    iterable: ExpressionAst


__all__ = ["LoopConditionIterableAst"]
