from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PostfixExpressionOperatorNotKeywordAst(Ast):
    tok_dot: TokenAst
    tok_not: TokenAst


__all__ = ["PostfixExpressionOperatorNotKeywordAst"]
