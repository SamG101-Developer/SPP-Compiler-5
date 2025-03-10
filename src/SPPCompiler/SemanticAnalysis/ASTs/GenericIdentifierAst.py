from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class GenericIdentifierAst(Ast):
    value: str = field(default="")
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default_factory=lambda: Asts.GenericArgumentGroupAst())

    def __post_init__(self) -> None:
        self.generic_argument_group.pos = self.generic_argument_group.pos or self.pos

    def __eq__(self, other: GenericIdentifierAst) -> bool:
        # Check both ASTs are the same type and have the same value and generic argument group.
        return isinstance(other, GenericIdentifierAst) and self.value == other.value and self.generic_argument_group == other.generic_argument_group

    def __hash__(self) -> int:
        # Hash the value into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5(self.value.encode()).digest())

    def __json__(self) -> str:
        return self.print(AstPrinter())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.value,
            self.generic_argument_group.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.generic_argument_group.pos_end

    @staticmethod
    def from_identifier(identifier: Asts.IdentifierAst) -> GenericIdentifierAst:
        return GenericIdentifierAst(identifier.pos, identifier.value)

    @staticmethod
    def from_type(type: Asts.TypeAst) -> GenericIdentifierAst:
        return type.type_parts()[0]

    def without_generics(self) -> GenericIdentifierAst:
        return GenericIdentifierAst(self.pos, self.value)


__all__ = ["GenericIdentifierAst"]
