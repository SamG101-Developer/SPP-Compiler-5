from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import hashlib, warnings

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class IdentifierAst(Ast):
    value: str

    def __eq__(self, other: IdentifierAst) -> bool:
        return isinstance(other, IdentifierAst) and self.value == other.value

    def __hash__(self):
        return int.from_bytes(hashlib.md5(self.value.encode()).digest())

    def __json__(self) -> str:
        return self.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.value

    @staticmethod
    def from_type(type: TypeAst) -> IdentifierAst:
        if type.namespace or type.types.length > 1:
            warnings.warn(f"Type {type} has a namespace or nested types, which will be ignored.")
        return IdentifierAst.from_generic_identifier(type.types[-1])

    @staticmethod
    def from_generic_identifier(identifier: GenericIdentifierAst) -> IdentifierAst:
        if identifier.generic_argument_group.arguments:
            warnings.warn(f"Generic identifier {identifier} has generic arguments, which will be ignored.")
        return IdentifierAst(identifier.pos, identifier.value)


__all__ = ["IdentifierAst"]
