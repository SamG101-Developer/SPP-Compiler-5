from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.PostfixExpressionAst import PostfixExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class BinaryExpressionAst(Ast):
    lhs: ExpressionAst
    op: TokenAst
    rhs: ExpressionAst
    _as_func: Optional[PostfixExpressionAst] = field(default=None, init=False, repr=False)


__all__ = ["BinaryExpressionAst"]
