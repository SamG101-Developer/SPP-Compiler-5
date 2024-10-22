from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class ObjectInitializerArgumentNamedAst(Ast):
    name: IdentifierAst | TokenAst  # attr= | else=, sup=
    assignment_token: TokenAst
    value: ExpressionAst


__all__ = ["ObjectInitializerArgumentNamedAst"]
