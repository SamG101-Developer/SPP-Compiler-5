from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type PrimaryExpressionAst = Union[
    Asts.LiteralAst,
    Asts.IdentifierAst,
    Asts.ParenthesizedExpressionAst,
    Asts.GenExpressionAst,
    Asts.ObjectInitializerAst,
    Asts.InnerScopeAst,
    Asts.CaseExpressionAst,
    Asts.LoopExpressionAst,
    Asts.WithExpressionAst,
    Asts.TypeAst,
    Asts.TokenAst,
]

__all__ = ["PrimaryExpressionAst"]
