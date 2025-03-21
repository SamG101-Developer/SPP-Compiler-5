from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

FunctionParameterAst = Union[
    Asts.FunctionParameterOptionalAst,
    Asts.FunctionParameterRequiredAst,
    Asts.FunctionParameterSelfAst,
    Asts.FunctionParameterVariadicAst]

__all__ = [
    "FunctionParameterAst"]
