from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

SupPrototypeAst = Union[
    Asts.SupPrototypeFunctionsAst,
    Asts.SupPrototypeExtensionAst
]

__all__ = [
    "SupPrototypeAst"]
