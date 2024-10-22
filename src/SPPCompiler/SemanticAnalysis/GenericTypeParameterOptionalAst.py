from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericParameterInlineConstraintAst import GenericParameterInlineConstraintAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class GenericTypeParameterOptionalAst(Ast):
    name: TypeAst
    constraints: GenericParameterInlineConstraintAst
    tok_assign: TokenAst
    default: TypeAst

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import TypeAst
        self.name = TypeAst.from_identifier(self.name)
        self.constraints = self.constraints or GenericParameterInlineConstraintAst.default()

    def __eq__(self, other: GenericTypeParameterOptionalAst) -> bool:
        return isinstance(other, GenericTypeParameterOptionalAst) and self.name == other.name


__all__ = ["GenericTypeParameterOptionalAst"]
