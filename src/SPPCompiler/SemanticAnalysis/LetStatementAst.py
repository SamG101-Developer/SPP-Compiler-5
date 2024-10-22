from typing import Union

from SPPCompiler.SemanticAnalysis.LetStatementInitializedAst import LetStatementInitializedAst
from SPPCompiler.SemanticAnalysis.LetStatementUninitializedAst import LetStatementUninitializedAst

type LetStatementAst = Union[
    LetStatementInitializedAst,
    LetStatementUninitializedAst]

__all__ = ["LetStatementAst"]
