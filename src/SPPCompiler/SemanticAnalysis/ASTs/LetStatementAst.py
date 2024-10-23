from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.LetStatementInitializedAst import LetStatementInitializedAst
from SPPCompiler.SemanticAnalysis.ASTs.LetStatementUninitializedAst import LetStatementUninitializedAst

type LetStatementAst = Union[
    LetStatementInitializedAst,
    LetStatementUninitializedAst]

__all__ = ["LetStatementAst"]
