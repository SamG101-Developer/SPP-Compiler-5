from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class Stage3_SupScopeLoader(ABC):
    @abstractmethod
    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        ...

    @abstractmethod
    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        ...


__all__ = ["Stage3_SupScopeLoader"]
