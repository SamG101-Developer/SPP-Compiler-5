from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class GenericIdentifierAst(Asts.Ast):
    value: str = field(default="")
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default=None)

    def __post_init__(self) -> None:
        self.generic_argument_group = self.generic_argument_group or Asts.GenericArgumentGroupAst(pos=0)
        if not self.generic_argument_group.pos:
            self.generic_argument_group.pos = self.pos + len(self.value)
            self.generic_argument_group.tok_r.pos = self.pos + len(self.value)

    def __eq__(self, other: GenericIdentifierAst) -> bool:
        # Check both ASTs are the same type and have the same value and generic argument group.
        return isinstance(other, GenericIdentifierAst) and self.value == other.value and self.generic_argument_group == other.generic_argument_group

    def __hash__(self) -> int:
        # Hash the value into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.sha256(self.value.encode()).digest())

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


__all__ = [
    "GenericIdentifierAst"]
