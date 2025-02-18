from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

ObjectInitializerArgumentAst = Union[
    Asts.ObjectInitializerArgumentUnnamedAst,
    Asts.ObjectInitializerArgumentNamedAst]

__all__ = ["ObjectInitializerArgumentAst"]
