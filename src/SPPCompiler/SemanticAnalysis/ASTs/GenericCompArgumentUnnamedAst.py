from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst


@dataclass
class GenericCompArgumentUnnamedAst(Ast):
    value: ExpressionAst

    def __eq__(self, other: GenericCompArgumentUnnamedAst) -> bool:
        return isinstance(other, GenericCompArgumentUnnamedAst) and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)


__all__ = ["GenericCompArgumentUnnamedAst"]
