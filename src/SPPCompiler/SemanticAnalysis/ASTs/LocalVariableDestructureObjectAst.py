from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableNestedForDestructureObjectAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class LocalVariableDestructureObjectAst(Ast):
    class_type: TypeAst
    tok_left_paren: TokenAst
    elements: Seq[LocalVariableNestedForDestructureObjectAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.elements = Seq(self.elements)


__all__ = ["LocalVariableDestructureObjectAst"]
