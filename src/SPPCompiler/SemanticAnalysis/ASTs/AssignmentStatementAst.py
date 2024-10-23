from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class AssignmentStatementAst(Ast):
    lhs: Seq[ExpressionAst]
    op: TokenAst
    rhs: Seq[ExpressionAst]

    def __post_init__(self) -> None:
        self.lhs = Seq(self.lhs)
        self.rhs = Seq(self.rhs)


__all__ = ["AssignmentStatementAst"]
