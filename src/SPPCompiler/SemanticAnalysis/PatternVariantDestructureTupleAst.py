from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.PatternVariantAst import PatternVariantNestedForDestructureTupleAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PatternVariantDestructureTupleAst(Ast):
    tok_left_paren: TokenAst
    elements: Seq[PatternVariantNestedForDestructureTupleAst]
    tok_right_paren: TokenAst


__all__ = ["PatternVariantDestructureTupleAst"]
