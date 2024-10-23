from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.GenericCompArgumentNamedAst import GenericCompArgumentNamedAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericCompArgumentUnnamedAst import GenericCompArgumentUnnamedAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericTypeArgumentNamedAst import GenericTypeArgumentNamedAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericTypeArgumentUnnamedAst import GenericTypeArgumentUnnamedAst

type GenericArgumentAst = Union[
    GenericCompArgumentNamedAst,
    GenericCompArgumentUnnamedAst,
    GenericTypeArgumentNamedAst,
    GenericTypeArgumentUnnamedAst]

type GenericCompArgumentAst = Union[
    GenericCompArgumentNamedAst,
    GenericCompArgumentUnnamedAst]

type GenericTypeArgumentAst = Union[
    GenericTypeArgumentNamedAst,
    GenericTypeArgumentUnnamedAst]

type GenericArgumentNamedAst = Union[
    GenericCompArgumentNamedAst,
    GenericTypeArgumentNamedAst]

type GenericArgumentUnnamedAst = Union[
    GenericCompArgumentUnnamedAst,
    GenericTypeArgumentUnnamedAst]

__all__ = [
    "GenericArgumentAst",
    "GenericArgumentNamedAst",
    "GenericArgumentUnnamedAst"]
