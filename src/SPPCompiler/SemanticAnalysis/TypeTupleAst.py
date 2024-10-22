from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class TypeTupleAst(Ast):
    tok_left_paren: TokenAst
    elements: Seq[TypeAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.elements = Seq(self.elements)

    def to_type(self) -> TypeAst:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        return CommonTypes.Tup(self.elements, self.tok_left_paren.pos)


__all__ = ["TypeTupleAst"]
