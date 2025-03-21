from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

ArrayLiteralAst = Union[
    Asts.ArrayLiteral0ElementAst,
    Asts.ArrayLiteralNElementAst]

__all__ = [
    "ArrayLiteralAst"]
