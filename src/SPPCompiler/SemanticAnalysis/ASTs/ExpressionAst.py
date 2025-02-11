from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type ExpressionAst = Union[
    Asts.BinaryExpressionAst,
    Asts.PostfixExpressionAst,
    Asts.UnaryExpressionAst,
    Asts.PrimaryExpressionAst]

__all__ = ["ExpressionAst"]
