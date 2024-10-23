from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.CaseExpressionAst import CaseExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class PatternVariantElseCaseAst(Ast):
    tok_else: TokenAst
    case_expression: CaseExpressionAst


__all__ = ["PatternVariantElseCaseAst"]
