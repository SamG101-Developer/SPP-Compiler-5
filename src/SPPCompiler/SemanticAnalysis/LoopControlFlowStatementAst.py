from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class LoopControlFlowStatementAst(Ast):
    tok_seq_exit: Seq[TokenAst]
    skip_or_expr: ExpressionAst

    def __post_init__(self) -> None:
        self.tok_seq_exit = Seq(self.tok_seq_exit)


__all__ = ["LoopControlFlowStatementAst"]
