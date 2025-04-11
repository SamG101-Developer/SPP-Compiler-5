from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

ExpressionAst = Union[
    Asts.BinaryExpressionAst,
    Asts.PostfixExpressionAst,
    Asts.UnaryExpressionAst,
    Asts.PrimaryExpressionAst]

__all__ = [
    "ExpressionAst"]
