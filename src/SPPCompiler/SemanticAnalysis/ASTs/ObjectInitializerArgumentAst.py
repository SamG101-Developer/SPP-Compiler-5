from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type ObjectInitializerArgumentAst = Union[
    Asts.ObjectInitializerArgumentUnnamedAst,
    Asts.ObjectInitializerArgumentNamedAst]

__all__ = ["ObjectInitializerArgumentAst"]
