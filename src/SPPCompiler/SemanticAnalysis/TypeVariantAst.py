from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class TypeVariantAst(Ast):
    elements: Seq[TypeAst]

    def __post_init__(self) -> None:
        self.elements = Seq(self.elements)

    def to_type(self) -> TypeAst:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        return CommonTypes.Var(self.elements, self.elements[0].pos)


__all__ = ["TypeVariantAst"]
