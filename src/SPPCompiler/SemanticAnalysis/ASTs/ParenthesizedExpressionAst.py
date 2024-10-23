from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class ParenthesizedExpressionAst(Ast):
    tok_left_paren: TokenAst
    expression: ExpressionAst
    tok_right_paren: TokenAst


__all__ = ["ParenthesizedExpressionAst"]
