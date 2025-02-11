from typing import Union

import SPPCompiler.SemanticAnalysis.ASTs as Asts

type LoopConditionAst = Union[
    Asts.LoopConditionBooleanAst,
    Asts.LoopConditionIterableAst]

__all__ = ["LoopConditionAst"]
