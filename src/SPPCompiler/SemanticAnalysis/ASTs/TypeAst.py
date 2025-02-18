from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

TypeAst = Union[
    Asts.TypeBinaryExpressionAst,
    Asts.TypePostfixExpressionAst,
    Asts.TypeUnaryExpressionAst,
    Asts.TypePrimaryExpressionAst
]

__all__ = ["TypeAst"]
