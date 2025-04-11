from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

LiteralAst = Union[
    Asts.ArrayLiteralAst,
    Asts.BooleanLiteralAst,
    Asts.FloatLiteralAst,
    Asts.IntegerLiteralAst,
    Asts.StringLiteralAst,
    Asts.TupleLiteralAst]

__all__ = [
    "LiteralAst"]
