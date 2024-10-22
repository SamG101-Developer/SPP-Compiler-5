from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class FunctionParameterOptionalAst(Ast):
    variable: LocalVariableAst
    tok_colon: TokenAst
    convention: ConventionAst
    type: TypeAst
    tok_assign: TokenAst
    default: ExpressionAst

    def __eq__(self, other: FunctionParameterOptionalAst) -> bool:
        return isinstance(other, FunctionParameterOptionalAst) and self.variable == other.variable


__all__ = ["FunctionParameterOptionalAst"]
