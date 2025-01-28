from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeExtensionAst import SupPrototypeExtensionAst

type SupPrototypeAst = Union[
    SupPrototypeFunctionsAst,
    SupPrototypeExtensionAst
]

__all__ = ["SupPrototypeAst"]
