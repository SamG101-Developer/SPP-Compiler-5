from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PostfixExpressionOperatorMemberAccessAst(Ast):
    tok_access: TokenAst
    attribute: IdentifierAst | TokenAst


__all__ = ["PostfixExpressionOperatorMemberAccessAst"]
