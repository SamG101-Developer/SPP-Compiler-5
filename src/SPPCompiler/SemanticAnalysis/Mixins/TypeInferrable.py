from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class TypeInferrable:
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        ...


@dataclass
class InferredTypeInfo:
    type: Asts.TypeAst
    convention: Asts.ConventionAst = field(default_factory=lambda: Asts.ConventionMovAst())

    def symbolic_eq(self, that: InferredTypeInfo, self_scope: Scope, that_scope: Optional[Scope] = None) -> bool:
        return type(self.convention) is type(that.convention) and self.type.symbolic_eq(that.type, self_scope, that_scope)

    def without_generics(self) -> InferredTypeInfo:
        return InferredTypeInfo(self.type.without_generics(), self.convention)
