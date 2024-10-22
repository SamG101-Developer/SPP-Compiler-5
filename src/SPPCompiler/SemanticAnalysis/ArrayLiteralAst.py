from typing import Union

from SPPCompiler.SemanticAnalysis.ArrayLiteral0ElementAst import ArrayLiteral0ElementAst
from SPPCompiler.SemanticAnalysis.ArrayLiteralNElementAst import ArrayLiteralNElementAst

type ArrayLiteralAst = Union[
    ArrayLiteral0ElementAst,
    ArrayLiteralNElementAst]

__all__ = ["ArrayLiteralAst"]
