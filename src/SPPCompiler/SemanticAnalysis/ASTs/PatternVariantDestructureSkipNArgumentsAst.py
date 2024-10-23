from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantSingleIdentifierAst import PatternVariantSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class PatternVariantDestructureSkipNArgumentsAst(Ast):
    variadic_token: TokenAst
    binding: Optional[PatternVariantSingleIdentifierAst]


__all__ = ["PatternVariantDestructureSkipNArgumentsAst"]
