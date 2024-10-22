from typing import Union

from SPPCompiler.SemanticAnalysis.ObjectInitializerArgumentUnnamedAst import ObjectInitializerArgumentUnnamedAst
from SPPCompiler.SemanticAnalysis.ObjectInitializerArgumentNamedAst import ObjectInitializerArgumentNamedAst

type ObjectInitializerArgumentAst = Union[
    ObjectInitializerArgumentUnnamedAst,
    ObjectInitializerArgumentNamedAst]

__all__ = ["ObjectInitializerArgumentAst"]
