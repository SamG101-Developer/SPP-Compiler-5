from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class AssignmentStatementAst(Ast):
    lhs: Seq[ExpressionAst]
    op: TokenAst
    rhs: Seq[ExpressionAst]


__all__ = ["AssignmentStatementAst"]
