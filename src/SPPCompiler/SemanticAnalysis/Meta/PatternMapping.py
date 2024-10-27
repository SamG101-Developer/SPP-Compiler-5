from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst


@dataclass
class PatternMapping(ABC):
    @abstractmethod
    def convert_to_variable(self, **kwargs) -> LocalVariableAst:
        ...
