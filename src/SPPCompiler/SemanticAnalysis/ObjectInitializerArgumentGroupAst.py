from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ObjectInitializerArgumentAst import ObjectInitializerArgumentAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class ObjectInitializerArgumentGroupAst(Ast):
    tok_left_paren: TokenAst
    arguments: Seq[ObjectInitializerArgumentAst]
    tok_right_paren: TokenAst


__all__ = ["ObjectInitializerArgumentGroupAst"]
