from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableNestedForAttributeBindingAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class LocalVariableAttributeBindingAst(Ast):
    name: IdentifierAst
    tok_assign: TokenAst
    value: LocalVariableNestedForAttributeBindingAst


__all__ = ["LocalVariableAttributeBindingAst"]
