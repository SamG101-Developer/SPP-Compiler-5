from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

ArrayLiteralAst = Union[
    Asts.ArrayLiteralRepeatedElementAst,
    Asts.ArrayLiteralExplicitElementsAst]
"""An ArrayLiteralAst is either a repeated-element or an explicit-element array."""

__all__ = [
    "ArrayLiteralAst"]
