from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class PatternVariantSingleIdentifierAst(Ast):
    mut_tok: Optional[TokenAst]
    name: IdentifierAst


__all__ = ["PatternVariantSingleIdentifierAst"]
