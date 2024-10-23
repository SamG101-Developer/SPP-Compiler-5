from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class RelStatementAst(Ast):
    tok_rel: TokenAst
    expressions: Seq[ExpressionAst]

    def __post_init__(self) -> None:
        self.expressions = Seq(self.expressions)


__all__ = ["RelStatementAst"]
