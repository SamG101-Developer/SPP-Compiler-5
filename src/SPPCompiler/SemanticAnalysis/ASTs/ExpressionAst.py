from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

ExpressionAst = Union[
    Asts.BinaryExpressionAst,
    Asts.PostfixExpressionAst,
    Asts.UnaryExpressionAst,
    Asts.PrimaryExpressionAst]

__all__ = ["ExpressionAst"]
