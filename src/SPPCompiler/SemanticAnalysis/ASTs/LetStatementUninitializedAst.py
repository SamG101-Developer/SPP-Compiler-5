from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class LetStatementUninitializedAst(Ast):
    tok_let: TokenAst
    tok_assign: LocalVariableAst
    tok_colon: TokenAst
    type: TypeAst


__all__ = ["LetStatementUninitializedAst"]
