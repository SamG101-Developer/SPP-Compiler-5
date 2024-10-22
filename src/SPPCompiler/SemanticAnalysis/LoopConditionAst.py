from typing import Union

from LoopConditionBooleanAst import LoopConditionBooleanAst
from LoopConditionIterableAst import LoopConditionIterableAst

type LoopConditionAst = Union[
    LoopConditionBooleanAst,
    LoopConditionIterableAst]

__all__ = ["LoopConditionAst"]
