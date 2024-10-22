from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class TypeOptionalAst(Ast):
    tok_qst: TokenAst
    type: TypeAst

    def to_type(self) -> TypeAst:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        return CommonTypes.Opt(self.type, self.type.pos)


__all__ = ["TypeOptionalAst"]
