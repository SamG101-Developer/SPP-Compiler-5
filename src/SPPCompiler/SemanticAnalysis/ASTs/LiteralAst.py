from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.ArrayLiteralAst import ArrayLiteralAst
from SPPCompiler.SemanticAnalysis.ASTs.BooleanLiteralAst import BooleanLiteralAst
from SPPCompiler.SemanticAnalysis.ASTs.FloatLiteralAst import FloatLiteralAst
from SPPCompiler.SemanticAnalysis.ASTs.IntegerLiteralAst import IntegerLiteralAst
from SPPCompiler.SemanticAnalysis.ASTs.StringLiteralAst import StringLiteralAst
from SPPCompiler.SemanticAnalysis.ASTs.TupleLiteralAst import TupleLiteralAst

type LiteralAst = Union[
    ArrayLiteralAst,
    BooleanLiteralAst,
    FloatLiteralAst,
    IntegerLiteralAst,
    StringLiteralAst,
    TupleLiteralAst]

__all__ = ["LiteralAst"]
