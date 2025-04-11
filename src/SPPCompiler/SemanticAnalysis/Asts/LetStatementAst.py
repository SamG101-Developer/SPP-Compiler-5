from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

LetStatementAst = Union[
    Asts.LetStatementInitializedAst,
    Asts.LetStatementUninitializedAst]

__all__ = [
    "LetStatementAst"]
