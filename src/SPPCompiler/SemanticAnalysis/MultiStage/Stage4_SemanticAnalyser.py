from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class Stage4_SemanticAnalyser(ABC):
    @abstractmethod
    def analyse_semantics(self, scope_handler: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["Stage4_SemanticAnalyser"]
