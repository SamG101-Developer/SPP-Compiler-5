from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

SupPrototypeAst = Union[
    Asts.SupPrototypeFunctionsAst,
    Asts.SupPrototypeExtensionAst
]

__all__ = ["SupPrototypeAst"]
