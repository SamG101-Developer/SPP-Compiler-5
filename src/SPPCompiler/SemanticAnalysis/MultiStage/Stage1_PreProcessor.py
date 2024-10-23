from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast


type PreProcessingContext = Optional[Ast]


@dataclass
class Stage1_PreProcessor(ABC):
    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)

    @abstractmethod
    def pre_process(self, context: PreProcessingContext) -> None:
        self._ctx = context


__all__ = ["Stage1_PreProcessor", "PreProcessingContext"]
