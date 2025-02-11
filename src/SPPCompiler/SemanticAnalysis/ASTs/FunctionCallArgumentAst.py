from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type FunctionCallArgumentAst = Union[
    Asts.FunctionCallArgumentNamedAst,
    Asts.FunctionCallArgumentUnnamedAst]

__all__ = ["FunctionCallArgumentAst"]
