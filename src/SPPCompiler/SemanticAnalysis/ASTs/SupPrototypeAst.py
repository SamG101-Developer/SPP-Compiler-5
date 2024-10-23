from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeInheritanceAst import SupPrototypeInheritanceAst

type SupPrototypeAst = Union[
    SupPrototypeFunctionsAst,
    SupPrototypeInheritanceAst
]

__all__ = ["SupPrototypeAst"]
