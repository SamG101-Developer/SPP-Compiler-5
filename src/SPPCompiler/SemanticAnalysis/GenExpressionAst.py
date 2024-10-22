from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class GenExpressionAst(Ast):
    tok_gen: TokenAst
    tok_with: Optional[TokenAst]
    convention: ConventionAst
    expression: Optional[ExpressionAst]

    _coro_type: Optional[TypeAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis.ConventionMovAst import ConventionMovAst
        self.convention = self.convention or ConventionMovAst.default()


__all__ = ["GenExpressionAst"]
