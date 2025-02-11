from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type LiteralAst = Union[
    Asts.ArrayLiteralAst,
    Asts.BooleanLiteralAst,
    Asts.FloatLiteralAst,
    Asts.IntegerLiteralAst,
    Asts.StringLiteralAst,
    Asts.TupleLiteralAst]

__all__ = ["LiteralAst"]
