from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class LocalVariableDestructureSkip1ArgumentAst(Ast):
    tok_underscore: TokenAst


__all__ = ["LocalVariableDestructureSkip1ArgumentAst"]
