from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericTypeParameterInlineConstraintAst import GenericTypeParameterInlineConstraintAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class GenericTypeParameterVariadicAst(Ast):
    tok_variadic: TokenAst
    name: TypeAst
    constraints: GenericTypeParameterInlineConstraintAst

    def __post_init__(self):
        from SPPCompiler.SemanticAnalysis import TypeAst
        self.name = TypeAst.from_identifier(self.name)
        self.constraints = self.constraints or GenericTypeParameterInlineConstraintAst.default()

    def __eq__(self, other: GenericTypeParameterVariadicAst) -> bool:
        return isinstance(other, GenericTypeParameterVariadicAst) and self.name == other.name


__all__ = ["GenericTypeParameterVariadicAst"]
