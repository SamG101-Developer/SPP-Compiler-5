from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type SupPrototypeAst = Union[
    Asts.SupPrototypeFunctionsAst,
    Asts.SupPrototypeExtensionAst
]

__all__ = ["SupPrototypeAst"]
