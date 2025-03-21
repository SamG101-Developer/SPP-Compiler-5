from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

TypeAst = Union[
    Asts.TypeBinaryExpressionAst,
    Asts.TypePostfixExpressionAst,
    Asts.TypeUnaryExpressionAst,
    Asts.TypeSingleAst
]

__all__ = [
    "TypeAst"]
