from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

FunctionCallArgumentAst = Union[
    Asts.FunctionCallArgumentNamedAst,
    Asts.FunctionCallArgumentUnnamedAst]

__all__ = [
    "FunctionCallArgumentAst"]
