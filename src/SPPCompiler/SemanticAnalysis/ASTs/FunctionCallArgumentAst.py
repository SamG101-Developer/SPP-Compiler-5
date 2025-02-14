from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

FunctionCallArgumentAst = Union[
    Asts.FunctionCallArgumentNamedAst,
    Asts.FunctionCallArgumentUnnamedAst]

__all__ = ["FunctionCallArgumentAst"]
