from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class RetStatementAst(Ast):
    tok_ret: TokenAst
    expression: Optional[ExpressionAst]


__all__ = ["RetStatementAst"]
