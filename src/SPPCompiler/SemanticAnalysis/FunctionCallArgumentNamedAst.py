from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class FunctionCallArgumentNamedAst(Ast):
    name: IdentifierAst
    tok_assign: TokenAst
    convention: ConventionAst
    value: ExpressionAst

    def __eq__(self, other: FunctionCallArgumentNamedAst) -> bool:
        return isinstance(other, FunctionCallArgumentNamedAst) and self.name == other.name and self.value == other.value


__all__ = ["FunctionCallArgumentNamedAst"]
