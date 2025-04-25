from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

UseStatementAst = Union[
    Asts.UseStatementAliasAst,
    Asts.UseStatementReduxAst
]

__all__ = [
    "UseStatementAst"]
