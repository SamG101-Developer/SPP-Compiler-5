from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class ArrayLiteralNElementAst(Ast):
    tok_left_bracket: TokenAst
    elements: Seq[ExpressionAst]
    tok_right_bracket: TokenAst

    def __post_init__(self) -> None:
        self.elements = Seq(self.elements)

    def __eq__(self, other: ArrayLiteralNElementAst) -> bool:
        return self.elements == other.elements


__all__ = ["ArrayLiteralNElementAst"]
