from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import hashlib

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentGroupAst import GenericArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class GenericIdentifierAst(Ast):
    value: str
    generic_argument_group: GenericArgumentGroupAst

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst
        self.generic_argument_group = self.generic_argument_group or GenericArgumentGroupAst.default()

    @staticmethod
    def from_identifier(identifier: IdentifierAst) -> GenericIdentifierAst:
        return GenericIdentifierAst(identifier.pos, identifier.value, None)

    def __eq__(self, other: GenericIdentifierAst) -> bool:
        return isinstance(other, GenericIdentifierAst) and self.value == other.value and self.generic_argument_group == other.generic_argument_group

    def __hash__(self) -> int:
        return int.from_bytes(hashlib.md5(self.value.encode()).digest())

    def __json__(self) -> str:
        return self.print(AstPrinter())


__all__ = ["GenericIdentifierAst"]
