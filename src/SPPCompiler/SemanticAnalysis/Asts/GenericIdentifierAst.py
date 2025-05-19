from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache


@dataclass(slots=True)
class GenericIdentifierAst(Asts.Ast):
    value: str = field(default="")
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default=None)

    def __post_init__(self) -> None:
        self.generic_argument_group = self.generic_argument_group or Asts.GenericArgumentGroupAst(pos=0)

    def __eq__(self, other: GenericIdentifierAst) -> bool:
        if isinstance(other, GenericIdentifierAst):
            return self.value == other.value and self.generic_argument_group == other.generic_argument_group
        elif isinstance(other, Asts.IdentifierAst):
            return self.value == other.value
        elif isinstance(other, Asts.TypeSingleAst):
            return self.value == other.name.value
        return False

    def __hash__(self) -> int:
        # Convert the value into an integer
        return int.from_bytes(self.value.encode())

    def __deepcopy__(self, memodict=None) -> GenericIdentifierAst:
        # Create a deep copy of the AST.
        return GenericIdentifierAst(
            pos=self.pos, value=self.value, generic_argument_group=fast_deepcopy(self.generic_argument_group))

    def __json__(self) -> str:
        return self.print(AstPrinter())

    def __str__(self) -> str:
        string = [
            self.value,
            str(self.generic_argument_group)]
        return "".join(string)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.value,
            self.generic_argument_group.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.generic_argument_group.pos_end if self.generic_argument_group.arguments else self.pos + len(self.value)

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
