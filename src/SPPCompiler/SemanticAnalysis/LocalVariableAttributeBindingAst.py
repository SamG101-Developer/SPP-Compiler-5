from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.LocalVariableAst import LocalVariableNestedForAttributeBindingAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class LocalVariableAttributeBindingAst(Ast):
    name: IdentifierAst
    tok_assign: TokenAst
    value: LocalVariableNestedForAttributeBindingAst


__all__ = ["LocalVariableAttributeBindingAst"]
