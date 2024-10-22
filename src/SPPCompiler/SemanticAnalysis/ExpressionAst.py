from typing import Union

from SPPCompiler.SemanticAnalysis.BinaryExpressionAst import BinaryExpressionAst
from SPPCompiler.SemanticAnalysis.PostfixExpressionAst import PostfixExpressionAst
from SPPCompiler.SemanticAnalysis.UnaryExpressionAst import UnaryExpressionAst
from SPPCompiler.SemanticAnalysis.PrimaryExpressionAst import PrimaryExpressionAst

type ExpressionAst = Union[
    BinaryExpressionAst,
    PostfixExpressionAst,
    UnaryExpressionAst,
    PrimaryExpressionAst]

__all__ = ["ExpressionAst"]
