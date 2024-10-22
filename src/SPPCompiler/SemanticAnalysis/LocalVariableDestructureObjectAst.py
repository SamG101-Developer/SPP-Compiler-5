from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableNestedForDestructureObjectAst


@dataclass
class LocalVariableDestructureObjectAst(Ast):
    class_type: TypeAst
    paren_l_token: TokenAst
    items: Seq[LocalVariableNestedForDestructureObjectAst]
    paren_r_token: TokenAst


__all__ = ["LocalVariableDestructureObjectAst"]
