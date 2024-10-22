from typing import Union

from SPPCompiler.SemanticAnalysis.CaseExpressionAst import CaseExpressionAst
from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
from SPPCompiler.SemanticAnalysis.InnerScopeAst import InnerScopeAst
from SPPCompiler.SemanticAnalysis.GenExpressionAst import GenExpressionAst
from SPPCompiler.SemanticAnalysis.LiteralAst import LiteralAst
from SPPCompiler.SemanticAnalysis.LoopExpressionAst import LoopExpressionAst
from SPPCompiler.SemanticAnalysis.ObjectInitializerAst import ObjectInitializerAst
from SPPCompiler.SemanticAnalysis.ParenthesizedExpressionAst import ParenthesizedExpressionAst
from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
from SPPCompiler.SemanticAnalysis.WithExpressionAst import WithExpressionAst

type PrimaryExpressionAst = Union[
    LiteralAst,
    IdentifierAst,
    ParenthesizedExpressionAst,
    GenExpressionAst,
    ObjectInitializerAst,
    InnerScopeAst,
    CaseExpressionAst,
    LoopExpressionAst,
    WithExpressionAst,
    TypeAst,
    TokenAst,
]

__all__ = ["PrimaryExpressionAst"]
