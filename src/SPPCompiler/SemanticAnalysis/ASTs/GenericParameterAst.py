from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.GenericCompParameterOptionalAst import GenericCompParameterOptionalAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericCompParameterRequiredAst import GenericCompParameterRequiredAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericCompParameterVariadicAst import GenericCompParameterVariadicAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericTypeParameterOptionalAst import GenericTypeParameterOptionalAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericTypeParameterRequiredAst import GenericTypeParameterRequiredAst
from SPPCompiler.SemanticAnalysis.ASTs.GenericTypeParameterVariadicAst import GenericTypeParameterVariadicAst

type GenericParameterAst = Union[
    GenericCompParameterOptionalAst,
    GenericCompParameterRequiredAst,
    GenericCompParameterVariadicAst,
    GenericTypeParameterOptionalAst,
    GenericTypeParameterRequiredAst,
    GenericTypeParameterVariadicAst]

type GenericCompParameterAst = Union[
    GenericCompParameterOptionalAst,
    GenericCompParameterRequiredAst,
    GenericCompParameterVariadicAst]

type GenericTypeParameterAst = Union[
    GenericTypeParameterOptionalAst,
    GenericTypeParameterRequiredAst,
    GenericTypeParameterVariadicAst]

type GenericParameterRequiredAst = Union[
    GenericCompParameterRequiredAst,
    GenericTypeParameterRequiredAst]

type GenericParameterOptionalAst = Union[
    GenericCompParameterOptionalAst,
    GenericTypeParameterOptionalAst]

type GenericParameterVariadicAst = Union[
    GenericCompParameterVariadicAst,
    GenericTypeParameterVariadicAst]

__all__ = [
    "GenericParameterAst",
    "GenericCompParameterAst",
    "GenericTypeParameterAst",
    "GenericParameterRequiredAst",
    "GenericParameterOptionalAst",
    "GenericParameterVariadicAst"]
