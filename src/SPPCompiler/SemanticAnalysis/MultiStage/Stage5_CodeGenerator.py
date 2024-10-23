from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class Stage5_CodeGenerator(ABC):
    @abstractmethod
    def generate_llvm(self, scope_handler: ScopeManager, **kwargs) -> Any:
        ...


__all__ = ["Stage5_CodeGenerator"]
