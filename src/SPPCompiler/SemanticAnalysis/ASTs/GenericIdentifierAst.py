from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import hashlib

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter, ast_printer_method

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentGroupAst import GenericArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class GenericIdentifierAst(Ast):
    value: str
    generic_argument_group: GenericArgumentGroupAst

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst

        # Create defaults.
        self.generic_argument_group = self.generic_argument_group or GenericArgumentGroupAst.default()

    def __eq__(self, other: GenericIdentifierAst) -> bool:
        return isinstance(other, GenericIdentifierAst) and self.value == other.value and self.generic_argument_group == other.generic_argument_group

    def __hash__(self) -> int:
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

    @staticmethod
    def from_identifier(identifier: IdentifierAst) -> GenericIdentifierAst:
        return GenericIdentifierAst(identifier.pos, identifier.value, None)


__all__ = ["GenericIdentifierAst"]
