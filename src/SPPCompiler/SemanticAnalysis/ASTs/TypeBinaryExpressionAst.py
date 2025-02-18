from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeBinaryExpressionAst(Ast):
    lhs: Asts.TypeAst = field(default=None)
    op: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())
    rhs: Asts.TypeAst = field(default=None)

    def convert(self) -> Asts.TypeSingleAst:
        match self.op.token.token_type:
            case SppTokenType.KwOr:
                return CommonTypes.Var(Seq([self.lhs, self.rhs]), self.pos)
            case SppTokenType.KwAnd:
                return CommonTypes.Isc(Seq([self.lhs, self.rhs]), self.pos)
            case _:
                raise Exception(f"Invalid binary operator {self.op.token}")


__all__ = ["TypeBinaryExpressionAst"]
