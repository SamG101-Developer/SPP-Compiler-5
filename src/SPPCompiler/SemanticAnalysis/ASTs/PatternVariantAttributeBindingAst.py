from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantAst import PatternVariantNestedForAttributeBindingAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class PatternVariantAttributeBindingAst(Ast):
    name: IdentifierAst
    tok_assign: TokenAst
    value: PatternVariantNestedForAttributeBindingAst


__all__ = ["PatternVariantAttributeBindingAst"]
