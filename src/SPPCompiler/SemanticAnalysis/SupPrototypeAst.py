from typing import Union

from SPPCompiler.SemanticAnalysis.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
from SPPCompiler.SemanticAnalysis.SupPrototypeInheritanceAst import SupPrototypeInheritanceAst

type SupPrototypeAst = Union[
    SupPrototypeFunctionsAst,
    SupPrototypeInheritanceAst
]

__all__ = ["SupPrototypeAst"]
