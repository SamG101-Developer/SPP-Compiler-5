from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type ArrayLiteralAst = Union[
    Asts.ArrayLiteral0ElementAst,
    Asts.ArrayLiteralNElementAst]

__all__ = ["ArrayLiteralAst"]
