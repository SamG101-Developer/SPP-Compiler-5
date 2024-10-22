from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class UnaryExpressionOperatorAsyncAst(Ast):
    tok_async: TokenAst


__all__ = ["UnaryExpressionOperatorAsyncAst"]
