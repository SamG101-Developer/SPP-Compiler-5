from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.PatternVariantAst import PatternVariantNestedForDestructureObjectAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PatternVariantDestructureObjectAst(Ast):
    type: TypeAst
    tok_left_paren: TokenAst
    elements: Seq[PatternVariantNestedForDestructureObjectAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.elements = Seq(self.elements)


__all__ = ["PatternVariantDestructureObjectAst"]
