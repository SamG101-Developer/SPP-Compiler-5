from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PatternVariantDestructureSkip1ArgumentAst(Ast):
    underscore_token: TokenAst


__all__ = ["PatternVariantDestructureSkip1ArgumentAst"]
