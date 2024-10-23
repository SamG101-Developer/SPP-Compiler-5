from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericTypeParameterInlineConstraintsAst import GenericTypeParameterInlineConstraintsAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class GenericTypeParameterVariadicAst(Ast):
    tok_variadic: TokenAst
    name: TypeAst
    constraints: GenericTypeParameterInlineConstraintsAst

    def __post_init__(self):
        from SPPCompiler.SemanticAnalysis import TypeAst, GenericTypeParameterInlineConstraintsAst
        self.name = TypeAst.from_identifier(self.name)
        self.constraints = self.constraints or GenericTypeParameterInlineConstraintsAst.default()

    def __eq__(self, other: GenericTypeParameterVariadicAst) -> bool:
        return isinstance(other, GenericTypeParameterVariadicAst) and self.name == other.name


__all__ = ["GenericTypeParameterVariadicAst"]
