from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

PrimaryExpressionAst = Union[
    Asts.LiteralAst,
    Asts.IdentifierAst,
    Asts.ParenthesizedExpressionAst,
    Asts.GenExpressionAst,
    Asts.ObjectInitializerAst,
    Asts.InnerScopeAst,
    Asts.CaseExpressionAst,
    Asts.LoopExpressionAst,
    Asts.TypeSingleAst,
    Asts.TokenAst,
]

__all__ = ["PrimaryExpressionAst"]
