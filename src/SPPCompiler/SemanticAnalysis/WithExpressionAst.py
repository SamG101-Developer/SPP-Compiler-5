from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.WithExpressionAliasAst import WithExpressionAliasAst
    from SPPCompiler.SemanticAnalysis.InnerScopeAst import InnerScopeAst


@dataclass
class WithExpressionAst(Ast):
    tok_with: TokenAst
    alias: Optional[WithExpressionAliasAst]
    expression: ExpressionAst
    body: InnerScopeAst[StatementAst]


__all__ = ["WithExpressionAst"]
