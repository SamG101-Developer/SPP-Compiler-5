from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class Stage2_SymbolGenerator(ABC):
    _scope: Optional[Scope] = field(default=None, kw_only=True, repr=False)

    @abstractmethod
    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        self._scope = scope_manager.current_scope


__all__ = ["Stage2_SymbolGenerator"]
