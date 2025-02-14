from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

GenericArgumentAst = Union[
    Asts.GenericCompArgumentNamedAst,
    Asts.GenericCompArgumentUnnamedAst,
    Asts.GenericTypeArgumentNamedAst,
    Asts.GenericTypeArgumentUnnamedAst]

GenericCompArgumentAst = Union[
    Asts.GenericCompArgumentNamedAst,
    Asts.GenericCompArgumentUnnamedAst]

GenericTypeArgumentAst = Union[
    Asts.GenericTypeArgumentNamedAst,
    Asts.GenericTypeArgumentUnnamedAst]

GenericArgumentNamedAst = Union[
    Asts.GenericCompArgumentNamedAst,
    Asts.GenericTypeArgumentNamedAst]

GenericArgumentUnnamedAst = Union[
    Asts.GenericCompArgumentUnnamedAst,
    Asts.GenericTypeArgumentUnnamedAst]

__all__ = [
    "GenericArgumentAst",
    "GenericCompArgumentAst",
    "GenericTypeArgumentAst",
    "GenericArgumentNamedAst",
    "GenericArgumentUnnamedAst"]
