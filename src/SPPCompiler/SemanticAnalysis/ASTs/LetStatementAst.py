from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type LetStatementAst = Union[
    Asts.LetStatementInitializedAst,
    Asts.LetStatementUninitializedAst]

__all__ = ["LetStatementAst"]
