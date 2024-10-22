from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.PatternBlockAst import PatternBlockAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class CaseExpressionAst(Ast):
    tok_case: TokenAst
    condition: ExpressionAst
    tok_then: TokenAst
    branches: Seq[PatternBlockAst]

    def __post_init__(self) -> None:
        self.branches = Seq(self.branches)


__all__ = ["CaseExpressionAst"]
