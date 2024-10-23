from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LiteralAst import LiteralAst


@dataclass
class PatternVariantLiteralAst(Ast):
    literal: LiteralAst


__all__ = ["PatternVariantLiteralAst"]