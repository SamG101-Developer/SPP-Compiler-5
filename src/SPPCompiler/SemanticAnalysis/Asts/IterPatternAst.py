from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

IterPatternAst = Union[
    Asts.IterPatternNoValueAst,
    Asts.IterPatternExceptionAst,
    Asts.IterPatternExhaustedAst,
    Asts.IterPatternVariableAst
]

__all__ = ["IterPatternAst"]
