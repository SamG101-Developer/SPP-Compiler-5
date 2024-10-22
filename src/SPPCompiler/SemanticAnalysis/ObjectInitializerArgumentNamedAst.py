from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst


@dataclass
class ObjectInitializerArgumentNamedAst(Ast):
    name: IdentifierAst | TokenAst
    assignment_token: TokenAst
    value: ExpressionAst


__all__ = ["ObjectInitializerArgumentNamedAst"]
