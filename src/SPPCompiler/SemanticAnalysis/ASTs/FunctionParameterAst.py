from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type FunctionParameterAst = Union[
    Asts.FunctionParameterOptionalAst,
    Asts.FunctionParameterRequiredAst,
    Asts.FunctionParameterSelfAst,
    Asts.FunctionParameterVariadicAst]

__all__ = ["FunctionParameterAst"]
