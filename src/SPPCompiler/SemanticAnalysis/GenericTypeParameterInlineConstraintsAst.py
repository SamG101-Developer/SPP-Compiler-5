from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class GenericTypeParameterInlineConstraintsAst(Ast):
    tok_colon: TokenAst
    constraints: Seq[TypeAst]

    def __post_init__(self) -> None:
        self.constraints = Seq(self.constraints)


__all__ = ["GenericTypeParameterInlineConstraintsAst"]
