from typing import Union

from SPPCompiler.SemanticAnalysis.FunctionParameterOptionalAst import FunctionParameterOptionalAst
from SPPCompiler.SemanticAnalysis.FunctionParameterRequiredAst import FunctionParameterRequiredAst
from SPPCompiler.SemanticAnalysis.FunctionParameterSelfAst import FunctionParameterSelfAst
from SPPCompiler.SemanticAnalysis.FunctionParameterVariadicAst import FunctionParameterVariadicAst

type FunctionParameterAst = Union[
    FunctionParameterOptionalAst,
    FunctionParameterRequiredAst,
    FunctionParameterSelfAst,
    FunctionParameterVariadicAst]

__all__ = ["FunctionParameterAst"]
