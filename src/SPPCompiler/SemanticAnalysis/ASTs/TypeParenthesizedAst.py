from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeParenthesizedAst(Ast):
    tok_l_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())
    type_expr: Asts.TypeAst = field(default_factory=Seq)
    tok_r_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())

    def convert(self) -> Asts.TypeSingleAst:
        return self.type_expr


__all__ = ["TypeParenthesizedAst"]
