from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import std

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst


@dataclass
class PatternMapping:
    @std.abstract_method
    def convert_to_variable(self, **kwargs) -> LocalVariableAst:
        ...
