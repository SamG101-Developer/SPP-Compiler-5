from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class Stage2_SymbolGenerator(ABC):
    @abstractmethod
    def generate_symbols(self, scope_handler: ScopeManager) -> None:
        ...


__all__ = ["Stage2_SymbolGenerator"]
