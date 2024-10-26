from __future__ import annotations
from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class ConventionMovAst(Ast, Default):
    def __eq__(self, other: ConventionMovAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, ConventionMovAst)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return ""

    @staticmethod
    def default() -> ConventionMovAst:
        return ConventionMovAst(-1)


__all__ = ["ConventionMovAst"]
