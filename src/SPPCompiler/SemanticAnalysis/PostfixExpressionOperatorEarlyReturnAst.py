from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PostfixExpressionOperatorEarlyReturnAst(Ast):
    tok_qst: TokenAst


__all__ = ["PostfixExpressionOperatorEarlyReturnAst"]
