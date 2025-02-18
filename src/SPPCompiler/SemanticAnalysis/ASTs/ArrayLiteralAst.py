from __future__ import annotations

from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

ArrayLiteralAst = Union[
    Asts.ArrayLiteral0ElementAst,
    Asts.ArrayLiteralNElementAst]

__all__ = ["ArrayLiteralAst"]
