from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

LoopConditionAst = Union[
    Asts.LoopConditionBooleanAst,
    Asts.LoopConditionIterableAst]

__all__ = [
    "LoopConditionAst"]
