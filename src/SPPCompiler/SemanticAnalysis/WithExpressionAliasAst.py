from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class WithExpressionAliasAst(Ast):
    variable: LocalVariableAst
    tok_assign: TokenAst


__all__ = ["WithExpressionAliasAst"]
