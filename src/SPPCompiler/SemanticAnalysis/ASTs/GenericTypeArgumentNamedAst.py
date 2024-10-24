from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class GenericTypeArgumentNamedAst(Ast):
    name: TypeAst
    tok_assign: TokenAst
    value: TypeAst

    def __eq__(self, other: GenericTypeArgumentNamedAst) -> bool:
        return isinstance(other, GenericTypeArgumentNamedAst) and self.name == other.name and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.value.print(printer)]
        return "".join(string)


__all__ = ["GenericTypeArgumentNamedAst"]
