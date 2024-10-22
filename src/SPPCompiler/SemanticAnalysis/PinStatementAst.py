from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PinStatementAst(Ast):
    tok_pin: TokenAst
    expressions: Seq[ExpressionAst]

    def __post_init__(self) -> None:
        self.expressions = Seq(self.expressions)


__all__ = ["PinStatementAst"]
