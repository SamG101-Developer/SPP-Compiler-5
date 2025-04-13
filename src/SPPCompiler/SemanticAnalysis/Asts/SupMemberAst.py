from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

SupMemberAst = Union[
    Asts.FunctionPrototypeAst,
    Asts.SupPrototypeExtensionAst,
    Asts.SupUseStatementAst,
    Asts.SupCmpStatementAst
]

__all__ = [
    "SupMemberAst"]
