from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type UnaryExpressionOperatorAst = Union[
    Asts.UnaryExpressionOperatorAsyncAst
]

__all__ = ["UnaryExpressionOperatorAst"]
