from typing import Union

from SPPCompiler.SemanticAnalysis.GenericCompArgumentNamedAst import GenericCompArgumentNamedAst
from SPPCompiler.SemanticAnalysis.GenericCompArgumentUnnamedAst import GenericCompArgumentUnnamedAst
from SPPCompiler.SemanticAnalysis.GenericTypeArgumentNamedAst import GenericTypeArgumentNamedAst
from SPPCompiler.SemanticAnalysis.GenericTypeArgumentUnnamedAst import GenericTypeArgumentUnnamedAst

type GenericArgumentAst = Union[
    GenericCompArgumentNamedAst,
    GenericCompArgumentUnnamedAst,
    GenericTypeArgumentNamedAst,
    GenericTypeArgumentUnnamedAst]

__all__ = ["GenericArgumentAst"]
