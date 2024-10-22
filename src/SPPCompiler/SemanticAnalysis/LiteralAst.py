from typing import Union

from SPPCompiler.SemanticAnalysis.ArrayLiteralAst import ArrayLiteralAst
from SPPCompiler.SemanticAnalysis.BooleanLiteralAst import BooleanLiteralAst
from SPPCompiler.SemanticAnalysis.FloatLiteralAst import FloatLiteralAst
from SPPCompiler.SemanticAnalysis.IntegerLiteralAst import IntegerLiteralAst
from SPPCompiler.SemanticAnalysis.RegexLiteralAst import RegexLiteralAst
from SPPCompiler.SemanticAnalysis.StringLiteralAst import StringLiteralAst
from SPPCompiler.SemanticAnalysis.TupleLiteralAst import TupleLiteralAst

type LiteralAst = Union[
    ArrayLiteralAst,
    BooleanLiteralAst,
    FloatLiteralAst,
    IntegerLiteralAst,
    RegexLiteralAst,
    StringLiteralAst,
    TupleLiteralAst]

__all__ = ["LiteralAst"]
