from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.LoopConditionBooleanAst import LoopConditionBooleanAst
from SPPCompiler.SemanticAnalysis.ASTs.LoopConditionIterableAst import LoopConditionIterableAst

type LoopConditionAst = Union[
    LoopConditionBooleanAst,
    LoopConditionIterableAst]

__all__ = ["LoopConditionAst"]
