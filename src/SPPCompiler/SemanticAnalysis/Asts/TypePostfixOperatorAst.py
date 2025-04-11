from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

TypePostfixOperatorAst = Union[
    Asts.TypePostfixOperatorNestedTypeAst,
    Asts.TypePostfixOperatorOptionalTypeAst,
]

__all__ = [
    "TypePostfixOperatorAst"]
