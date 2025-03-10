from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

TypeUnaryOperatorAst = Union[
    Asts.TypeUnaryOperatorNamespaceAst,
    Asts.TypeUnaryOperatorBorrowAst
]

__all__ = ["TypeUnaryOperatorAst"]
