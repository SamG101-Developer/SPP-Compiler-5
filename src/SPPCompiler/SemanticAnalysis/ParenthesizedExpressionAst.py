from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class ParenthesizedExpressionAst(Ast):
    tok_left_paren: TokenAst
    expression: ExpressionAst
    tok_right_paren: TokenAst


__all__ = ["ParenthesizedExpressionAst"]
