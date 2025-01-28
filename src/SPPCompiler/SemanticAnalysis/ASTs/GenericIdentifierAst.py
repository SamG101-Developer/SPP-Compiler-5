from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import hashlib, std


from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class GenericIdentifierAst(Ast):
    value: str = field(default="")
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default_factory=lambda: Asts.GenericArgumentGroupAst())

    @std.override_method
    def __eq__(self, other: GenericIdentifierAst) -> bool:
        # Check both ASTs are the same type and have the same value and generic argument group.
        return isinstance(other, GenericIdentifierAst) and self.value == other.value and self.generic_argument_group == other.generic_argument_group

    @std.override_method
    def __hash__(self) -> int:
        # Hash the value into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5(self.value.encode()).digest())

    def __json__(self) -> str:
        return self.print(AstPrinter())

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.value,
            self.generic_argument_group.print(printer)]
        return "".join(string)

    @staticmethod
    def from_identifier(identifier: Asts.IdentifierAst) -> GenericIdentifierAst:
        return GenericIdentifierAst(identifier.pos, identifier.value, Asts.GenericArgumentGroupAst())

    @staticmethod
    def from_type(type: TypeAst) -> GenericIdentifierAst:
        return type.types[-1]

    def without_generics(self) -> GenericIdentifierAst:
        return GenericIdentifierAst(self.pos, self.value, Asts.GenericArgumentGroupAst())


__all__ = ["GenericIdentifierAst"]
