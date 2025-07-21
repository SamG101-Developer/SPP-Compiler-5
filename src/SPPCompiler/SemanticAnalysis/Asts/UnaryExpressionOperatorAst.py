from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

UnaryExpressionOperatorAst = Union[
    Asts.UnaryExpressionOperatorAsyncAst,
    Asts.UnaryExpressionOperatorDerefAst
]

__all__ = [
    "UnaryExpressionOperatorAst"]
