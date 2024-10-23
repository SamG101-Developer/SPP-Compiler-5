from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class FunctionParameterRequiredAst(Ast):
    variable: LocalVariableAst
    tok_colon: TokenAst
    convention: ConventionAst
    type: TypeAst

    def __eq__(self, other: FunctionParameterRequiredAst) -> bool:
        return isinstance(other, FunctionParameterRequiredAst) and self.variable == other.variable


__all__ = ["FunctionParameterRequiredAst"]
