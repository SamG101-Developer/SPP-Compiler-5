from __future__ import annotations

from dataclasses import dataclass

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class TypeInferrable:
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        ...
