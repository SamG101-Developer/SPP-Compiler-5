from __future__ import annotations
from convert_case import pascal_case
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypePartAst import TypePartAst


@dataclass
class TypeAst(Ast):
    namespace: Seq[IdentifierAst]
    types: Seq[TypePartAst]

    def __post_init__(self) -> None:
        # Convert the namespace and types into a sequence.
        self.namespace = Seq(self.namespace)
        self.types = Seq(self.types)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.namespace.print(printer, "::") + "::" if self.namespace else "",
            self.types.print(printer, "::")]
        return "".join(string)

    @staticmethod
    def from_identifier(identifier: IdentifierAst) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, TypeAst
        return TypeAst(identifier.pos, Seq(), Seq([GenericIdentifierAst.from_identifier(identifier)]))

    @staticmethod
    def from_function_identifier(identifier: IdentifierAst) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        mock_type_name = IdentifierAst(identifier.pos, f"${pascal_case(identifier.value.replace("_", " "))}")
        return TypeAst.from_identifier(mock_type_name)


__all__ = ["TypeAst"]
