from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeTupleAst(Ast):
    tok_l_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())
    type_list: Seq[Asts.TypeAst] = field(default_factory=Seq)
    tok_r_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())

    @property
    def pos_end(self) -> int:
        return self.tok_r_paren.pos_end

    def convert(self) -> Asts.TypeSingleAst:
        return CommonTypes.Tup(self.type_list, self.pos)


__all__ = ["TypeTupleAst"]
