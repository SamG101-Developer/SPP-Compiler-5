from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.ObjectInitializerArgumentUnnamedAst import ObjectInitializerArgumentUnnamedAst
from SPPCompiler.SemanticAnalysis.ASTs.ObjectInitializerArgumentNamedAst import ObjectInitializerArgumentNamedAst

type ObjectInitializerArgumentAst = Union[
    ObjectInitializerArgumentUnnamedAst,
    ObjectInitializerArgumentNamedAst]

__all__ = ["ObjectInitializerArgumentAst"]
