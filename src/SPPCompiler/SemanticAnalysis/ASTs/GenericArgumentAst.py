from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type GenericArgumentAst = Union[
    Asts.GenericCompArgumentNamedAst,
    Asts.GenericCompArgumentUnnamedAst,
    Asts.GenericTypeArgumentNamedAst,
    Asts.GenericTypeArgumentUnnamedAst]

type GenericCompArgumentAst = Union[
    Asts.GenericCompArgumentNamedAst,
    Asts.GenericCompArgumentUnnamedAst]

type GenericTypeArgumentAst = Union[
    Asts.GenericTypeArgumentNamedAst,
    Asts.GenericTypeArgumentUnnamedAst]

type GenericArgumentNamedAst = Union[
    Asts.GenericCompArgumentNamedAst,
    Asts.GenericTypeArgumentNamedAst]

type GenericArgumentUnnamedAst = Union[
    Asts.GenericCompArgumentUnnamedAst,
    Asts.GenericTypeArgumentUnnamedAst]

__all__ = [
    "GenericArgumentAst",
    "GenericCompArgumentAst",
    "GenericTypeArgumentAst",
    "GenericArgumentNamedAst",
    "GenericArgumentUnnamedAst"]
