from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type GenericParameterAst = Union[
    Asts.GenericCompParameterOptionalAst,
    Asts.GenericCompParameterRequiredAst,
    Asts.GenericCompParameterVariadicAst,
    Asts.GenericTypeParameterOptionalAst,
    Asts.GenericTypeParameterRequiredAst,
    Asts.GenericTypeParameterVariadicAst]

type GenericCompParameterAst = Union[
    Asts.GenericCompParameterOptionalAst,
    Asts.GenericCompParameterRequiredAst,
    Asts.GenericCompParameterVariadicAst]

type GenericTypeParameterAst = Union[
    Asts.GenericTypeParameterOptionalAst,
    Asts.GenericTypeParameterRequiredAst,
    Asts.GenericTypeParameterVariadicAst]

type GenericParameterRequiredAst = Union[
    Asts.GenericCompParameterRequiredAst,
    Asts.GenericTypeParameterRequiredAst]

type GenericParameterOptionalAst = Union[
    Asts.GenericCompParameterOptionalAst,
    Asts.GenericTypeParameterOptionalAst]

type GenericParameterVariadicAst = Union[
    Asts.GenericCompParameterVariadicAst,
    Asts.GenericTypeParameterVariadicAst]

__all__ = [
    "GenericParameterAst",
    "GenericCompParameterAst",
    "GenericTypeParameterAst",
    "GenericParameterRequiredAst",
    "GenericParameterOptionalAst",
    "GenericParameterVariadicAst"]
