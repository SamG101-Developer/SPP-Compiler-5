from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.PostfixExpressionAst import PostfixExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class AnnotationAst(Ast):
    tok_at: TokenAst
    name: IdentifierAst | PostfixExpressionAst


__all__ = ["AnnotationAst"]
