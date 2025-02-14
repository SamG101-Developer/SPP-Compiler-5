from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

TypePrimaryExpressionAst = Union[
    Asts.TypeParenthesizedAst,
    Asts.TypeArrayAst,
    Asts.TypeTupleAst,
    Asts.TypeSingleAst,
]

__all__ = ["TypePrimaryExpressionAst"]
