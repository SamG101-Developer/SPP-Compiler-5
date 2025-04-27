from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

LambdaExpressionParameterAst = Union[
    Asts.FunctionParameterOptionalAst,
    Asts.FunctionParameterRequiredAst,
    Asts.FunctionParameterVariadicAst]

__all__ = [
    "LambdaExpressionParameterAst"]
