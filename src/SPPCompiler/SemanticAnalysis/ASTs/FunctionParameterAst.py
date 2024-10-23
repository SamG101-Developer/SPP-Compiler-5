from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterOptionalAst import FunctionParameterOptionalAst
from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterRequiredAst import FunctionParameterRequiredAst
from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterSelfAst import FunctionParameterSelfAst
from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterVariadicAst import FunctionParameterVariadicAst

type FunctionParameterAst = Union[
    FunctionParameterOptionalAst,
    FunctionParameterRequiredAst,
    FunctionParameterSelfAst,
    FunctionParameterVariadicAst]

__all__ = ["FunctionParameterAst"]
