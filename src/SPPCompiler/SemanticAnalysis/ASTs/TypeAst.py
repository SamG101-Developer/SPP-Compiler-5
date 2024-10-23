from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypePartAst import TypePartAst


@dataclass
class TypeAst(Ast):
    namespace: Seq[IdentifierAst]
    types: Seq[TypePartAst]

    def __post_init__(self):
        self.namespace = Seq(self.namespace)
        self.types = Seq(self.types)

    @staticmethod
    def from_identifier(identifier: IdentifierAst) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, TypeAst
        return TypeAst(identifier.pos, Seq(), Seq([GenericIdentifierAst.from_identifier(identifier)]))

    @staticmethod
    def from_function_identifier(identifier: IdentifierAst) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        mock_type_name = IdentifierAst(identifier.pos, f"${identifier.value[0].upper()}{identifier.value[1:]}")
        return TypeAst.from_identifier(mock_type_name)


__all__ = ["TypeAst"]
