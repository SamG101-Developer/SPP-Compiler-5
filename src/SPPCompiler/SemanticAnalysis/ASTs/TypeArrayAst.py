from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast


@dataclass
class TypeArrayAst(Ast):
    tok_l_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())
    type: Asts.TypeAst = field(default_factory=lambda: Asts.TypeSingleAst())
    comma: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkComma))
    size: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.LxNumber))
    tok_r_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())

    def convert(self) -> Asts.TypeSingleAst:
        return CommonTypes.Arr(self.type, self.size, self.pos)


__all__ = ["TypeArrayAst"]
