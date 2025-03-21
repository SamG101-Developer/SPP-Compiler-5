from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

TypeUnaryOperatorAst = Union[
    Asts.TypeUnaryOperatorNamespaceAst,
    Asts.TypeUnaryOperatorBorrowAst
]

__all__ = [
    "TypeUnaryOperatorAst"]
