from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.InnerScopeAst import InnerScopeAst
    from SPPCompiler.SemanticAnalysis.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class LoopElseStatementAst(Ast):
    tok_else: TokenAst
    body: InnerScopeAst[StatementAst]


__all__ = ["LoopElseStatementAst"]
