from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionOperatorAst import PostfixExpressionOperatorAst


@dataclass
class PostfixExpressionAst(Ast):
    lhs: ExpressionAst
    op: PostfixExpressionOperatorAst


__all__ = ["PostfixExpressionAst"]
