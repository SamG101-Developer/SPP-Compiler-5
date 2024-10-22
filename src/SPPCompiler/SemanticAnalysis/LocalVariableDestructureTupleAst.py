from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableNestedForDestructureTupleAst


@dataclass
class LocalVariableDestructureTupleAst(Ast):
    tok_left_paren: TokenAst
    elements: Seq[LocalVariableNestedForDestructureTupleAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.elements = Seq(self.elements)


__all__ = ["LocalVariableDestructureTupleAst"]
