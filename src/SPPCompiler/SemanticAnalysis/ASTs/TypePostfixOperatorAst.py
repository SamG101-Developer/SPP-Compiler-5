from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

TypePostfixOperatorAst = Union[
    Asts.TypePostfixOperatorNestedTypeAst,
    Asts.TypePostfixOperatorIndexedTypeAst,
    Asts.TypePostfixOperatorOptionalTypeAst,
]

__all__ = ["TypePostfixOperatorAst"]
