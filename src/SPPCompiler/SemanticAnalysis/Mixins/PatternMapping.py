from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import std

if TYPE_CHECKING:
    import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class PatternMapping:
    @std.abstract_method
    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableAst:
        ...
