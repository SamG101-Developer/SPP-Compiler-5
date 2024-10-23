from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.PatternGuardAst import PatternGuardAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantAst import PatternVariantAst
    from SPPCompiler.SemanticAnalysis.ASTs.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst


@dataclass
class PatternBlockAst(Ast):
    comp_operator: TokenAst
    patterns: Seq[PatternVariantAst]
    guard: Optional[PatternGuardAst]
    body: InnerScopeAst[StatementAst]

    def __post_init__(self) -> None:
        self.patterns = Seq(self.patterns)


__all__ = ["PatternBlockAst"]
