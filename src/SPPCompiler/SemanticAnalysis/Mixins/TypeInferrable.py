from __future__ import annotations
from dataclasses import dataclass
from typing import Type, TYPE_CHECKING
import std

if TYPE_CHECKING:
    import SPPCompiler.SemanticAnalysis as Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass(kw_only=True)
class InferredType:
    convention: Type[Asts.ConventionAst]
    type: Asts.TypeAst

    def __str__(self) -> str:
        return f"{self.convention()}{self.type}"

    def __hash__(self) -> int:
        return hash(self.type)

    def symbolic_eq(self, that: InferredType, self_scope: Scope, that_scope: Scope = None) -> bool:
        return self.convention is that.convention and self.type.symbolic_eq(that.type, self_scope, that_scope)

    def without_generics(self) -> InferredType:
        return InferredType(convention=self.convention, type=self.type.without_generics())

    @staticmethod
    def from_type(type: Asts.TypeAst) -> InferredType:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst
        return InferredType(convention=ConventionMovAst, type=type)


@dataclass
class TypeInferrable:
    @std.abstract_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...
