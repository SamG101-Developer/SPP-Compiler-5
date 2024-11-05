from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionMovAst import ConventionMovAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass(kw_only=True)
class InferredType:
    convention: Type[ConventionAst]
    type: TypeAst

    def __str__(self) -> str:
        return f"{self.convention.default()}{self.type}"

    def symbolic_eq(self, that: InferredType, self_scope: Scope, that_scope: Scope = None) -> bool:
        return self.convention is that.convention and self.type.symbolic_eq(that.type, self_scope, that_scope)

    def without_generics(self) -> InferredType:
        return InferredType(convention=self.convention, type=self.type.without_generics())

    @staticmethod
    def from_type(type: TypeAst) -> InferredType:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst
        return InferredType(convention=ConventionMovAst, type=type)


@dataclass
class TypeInferrable(ABC):
    @abstractmethod
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...
