from typing import Union

from SPPCompiler.SemanticAnalysis.FunctionCallArgumentNamedAst import FunctionCallArgumentNamedAst
from SPPCompiler.SemanticAnalysis.FunctionCallArgumentUnnamedAst import FunctionCallArgumentUnnamedAst

type FunctionCallArgumentAst = Union[
    FunctionCallArgumentNamedAst,
    FunctionCallArgumentUnnamedAst]

__all__ = ["FunctionCallArgumentAst"]
