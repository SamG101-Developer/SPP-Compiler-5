from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentNamedAst import FunctionCallArgumentNamedAst
from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentUnnamedAst import FunctionCallArgumentUnnamedAst

type FunctionCallArgumentAst = Union[
    FunctionCallArgumentNamedAst,
    FunctionCallArgumentUnnamedAst]

__all__ = ["FunctionCallArgumentAst"]
