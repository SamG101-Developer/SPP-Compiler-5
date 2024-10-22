from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class LetStatementUninitializedAst(Ast):
    tok_let: TokenAst
    tok_assign: LocalVariableAst
    tok_colon: TokenAst
    type: TypeAst


__all__ = ["LetStatementUninitializedAst"]
