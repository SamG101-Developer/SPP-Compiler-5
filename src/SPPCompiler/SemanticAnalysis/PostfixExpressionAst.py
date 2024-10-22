from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.PostfixExpressionOperatorAst import PostfixExpressionOperatorAst


@dataclass
class PostfixExpressionAst(Ast):
    lhs: ExpressionAst
    op: PostfixExpressionOperatorAst


__all__ = ["PostfixExpressionAst"]
