from typing import Union

from SPPCompiler.SemanticAnalysis.LoopConditionBooleanAst import LoopConditionBooleanAst
from SPPCompiler.SemanticAnalysis.LoopConditionIterableAst import LoopConditionIterableAst

type LoopConditionAst = Union[
    LoopConditionBooleanAst,
    LoopConditionIterableAst]

__all__ = ["LoopConditionAst"]
