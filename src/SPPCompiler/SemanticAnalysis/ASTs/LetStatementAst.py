from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

LetStatementAst = Union[
    Asts.LetStatementInitializedAst,
    Asts.LetStatementUninitializedAst]

__all__ = ["LetStatementAst"]
