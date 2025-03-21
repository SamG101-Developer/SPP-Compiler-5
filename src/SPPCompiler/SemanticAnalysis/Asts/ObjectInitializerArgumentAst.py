from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

ObjectInitializerArgumentAst = Union[
    Asts.ObjectInitializerArgumentUnnamedAst,
    Asts.ObjectInitializerArgumentNamedAst]

__all__ = [
    "ObjectInitializerArgumentAst"]
