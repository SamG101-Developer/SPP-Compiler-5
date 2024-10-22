from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericParameterInlineConstraintAst import GenericParameterInlineConstraintAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class GenericTypeParameterRequiredAst(Ast):
    name: TypeAst
    inline_constraints: GenericParameterInlineConstraintAst

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import TypeAst
        self.name = TypeAst.from_identifier(self.name)
        self.inline_constraints = self.inline_constraints or GenericParameterInlineConstraintAst.default()

    def __eq__(self, other: GenericTypeParameterRequiredAst) -> bool:
        return isinstance(other, GenericTypeParameterRequiredAst) and self.name == other.name
    
    
__all__ = ["GenericTypeParameterRequiredAst"]
