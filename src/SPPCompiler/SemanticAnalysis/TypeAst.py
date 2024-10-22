from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq


if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TypePartAst import TypePartAst


@dataclass
class TypeAst(Ast):
    namespace: Seq[IdentifierAst]
    types: Seq[TypePartAst]

    def __post_init__(self):
        self.namespace = self.namespace or Seq()

    @staticmethod
    def from_identifier(identifier: IdentifierAst) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, TypeAst
        return TypeAst(identifier.pos, Seq(), Seq([GenericIdentifierAst.from_identifier(identifier)]))


__all__ = ["TypeAst"]
