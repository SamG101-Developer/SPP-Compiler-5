from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst


@dataclass
class PatternMapping:
    def convert_to_variable(self, **kwargs) -> LocalVariableAst:
        ...
