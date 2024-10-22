from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class RelStatementAst(Ast):
    tok_rel: TokenAst
    expressions: Seq[ExpressionAst]


__all__ = ["RelStatementAst"]
