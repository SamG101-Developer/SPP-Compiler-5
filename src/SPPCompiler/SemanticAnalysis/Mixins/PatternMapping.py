from __future__ import annotations

from dataclasses import dataclass

import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class PatternMapping:
    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableAst:
        ...
