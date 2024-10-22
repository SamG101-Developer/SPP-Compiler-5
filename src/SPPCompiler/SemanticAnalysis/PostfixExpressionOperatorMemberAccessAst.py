from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.PostfixMemberPartAst import PostfixMemberPartAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PostfixExpressionOperatorMemberAccessAst(Ast):
    tok_access: TokenAst
    attribute: PostfixMemberPartAst


__all__ = ["PostfixExpressionOperatorMemberAccessAst"]
