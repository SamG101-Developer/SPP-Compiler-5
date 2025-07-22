from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

TypeAst = Union[
    Asts.TypeBinaryExpressionAst,
    Asts.TypePostfixExpressionAst,
    Asts.TypeUnaryExpressionAst,
    Asts.TypeIdentifierAst
]

__all__ = [
    "TypeAst"]
