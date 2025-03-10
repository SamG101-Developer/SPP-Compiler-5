from __future__ import annotations

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class TypeInferrable:
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        ...
