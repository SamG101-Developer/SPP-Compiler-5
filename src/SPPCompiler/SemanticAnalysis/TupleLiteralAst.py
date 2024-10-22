from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class TupleLiteralAst(Ast):
    tok_left_paren: TokenAst
    elements: Seq[ExpressionAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.elements = Seq(self.elements)


__all__ = ["TupleLiteralAst"]
