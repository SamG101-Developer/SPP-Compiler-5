from __future__ import annotations
from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast


@dataclass
class FunctionParameterVariadicAst(Ast):
    tok_variadic: TokenAst
    variable: LocalVariableAst
    tok_colon: TokenAst
    convention: ConventionAst
    type: TypeAst

    def __eq__(self, other: FunctionParameterVariadicAst) -> bool:
        return isinstance(other, FunctionParameterVariadicAst) and self.variable == other.variable


__all__ = ["FunctionParameterVariadicAst"]
