from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class FunctionParameterRequiredAst(Ast):
    variable: LocalVariableAst
    tok_colon: TokenAst
    convention: ConventionAst
    type: TypeAst

    def __eq__(self, other: FunctionParameterRequiredAst) -> bool:
        return isinstance(other, FunctionParameterRequiredAst) and self.variable == other.variable


__all__ = ["FunctionParameterRequiredAst"]
