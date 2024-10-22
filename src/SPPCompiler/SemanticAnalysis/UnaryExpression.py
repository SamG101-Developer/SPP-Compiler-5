from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.UnaryOperatorAst import UnaryOperatorAst


@dataclass
class UnaryExpressionAst(Ast):
    op: UnaryOperatorAst
    rhs: ExpressionAst


__all__ = ["UnaryExpressionAst"]
