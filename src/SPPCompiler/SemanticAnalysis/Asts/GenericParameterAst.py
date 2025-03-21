from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

GenericParameterAst = Union[
    Asts.GenericCompParameterOptionalAst,
    Asts.GenericCompParameterRequiredAst,
    Asts.GenericCompParameterVariadicAst,
    Asts.GenericTypeParameterOptionalAst,
    Asts.GenericTypeParameterRequiredAst,
    Asts.GenericTypeParameterVariadicAst]

GenericCompParameterAst = Union[
    Asts.GenericCompParameterOptionalAst,
    Asts.GenericCompParameterRequiredAst,
    Asts.GenericCompParameterVariadicAst]

GenericTypeParameterAst = Union[
    Asts.GenericTypeParameterOptionalAst,
    Asts.GenericTypeParameterRequiredAst,
    Asts.GenericTypeParameterVariadicAst]

GenericParameterRequiredAst = Union[
    Asts.GenericCompParameterRequiredAst,
    Asts.GenericTypeParameterRequiredAst]

GenericParameterOptionalAst = Union[
    Asts.GenericCompParameterOptionalAst,
    Asts.GenericTypeParameterOptionalAst]

GenericParameterVariadicAst = Union[
    Asts.GenericCompParameterVariadicAst,
    Asts.GenericTypeParameterVariadicAst]

__all__ = [
    "GenericParameterAst",
    "GenericCompParameterAst",
    "GenericTypeParameterAst",
    "GenericParameterRequiredAst",
    "GenericParameterOptionalAst",
    "GenericParameterVariadicAst"]
