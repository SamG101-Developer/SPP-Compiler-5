from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class WhereConstraintsAst(Ast):
    types: Seq[TypeAst]
    tok_colon: TokenAst
    constraints: Seq[TypeAst]

    def __post_init__(self) -> None:
        self.types = Seq(self.types)
        self.constraints = Seq(self.constraints)


__all__ = ["WhereConstraintsAst"]
