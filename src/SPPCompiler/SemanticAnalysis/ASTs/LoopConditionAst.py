from typing import Union

import SPPCompiler.SemanticAnalysis.ASTs as Asts

LoopConditionAst = Union[
    Asts.LoopConditionBooleanAst,
    Asts.LoopConditionIterableAst]

__all__ = ["LoopConditionAst"]
