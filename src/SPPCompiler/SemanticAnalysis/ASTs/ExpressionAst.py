from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.BinaryExpressionAst import BinaryExpressionAst
from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionAst import PostfixExpressionAst
from SPPCompiler.SemanticAnalysis.ASTs.UnaryExpressionAst import UnaryExpressionAst
from SPPCompiler.SemanticAnalysis.ASTs.PrimaryExpressionAst import PrimaryExpressionAst

type ExpressionAst = Union[
    BinaryExpressionAst,
    PostfixExpressionAst,
    UnaryExpressionAst,
    PrimaryExpressionAst]

__all__ = ["ExpressionAst"]
