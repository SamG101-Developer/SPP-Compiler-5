from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

PrimaryExpressionAst = Union[
    Asts.LiteralAst,
    Asts.IdentifierAst,
    Asts.ParenthesizedExpressionAst,
    Asts.GenExpressionAst,
    Asts.GenWithExpressionAst,
    Asts.ObjectInitializerAst,
    Asts.InnerScopeAst,
    Asts.CaseExpressionAst,
    Asts.LoopExpressionAst,
    Asts.TypeSingleAst,
    Asts.TokenAst,
]

__all__ = [
    "PrimaryExpressionAst"]
