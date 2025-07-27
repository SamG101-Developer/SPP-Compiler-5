from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

ArrayLiteralAst = Union[
    Asts.ArrayLiteralRepeatedElementAst,
    Asts.ArrayLiteralExplicitElementsAst]
"""An ArrayLiteralAst is either a 0-element (empty) or n-element (filled) array."""

__all__ = [
    "ArrayLiteralAst"]
