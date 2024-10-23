from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.UnaryExpressionOperatorAst import UnaryExpressionOperatorAst


@dataclass
class UnaryExpressionAst(Ast):
    op: UnaryExpressionOperatorAst
    rhs: ExpressionAst


__all__ = ["UnaryExpressionAst"]
