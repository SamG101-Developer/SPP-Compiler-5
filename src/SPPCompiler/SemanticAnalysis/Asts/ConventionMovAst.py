from __future__ import annotations

from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class ConventionMovAst(Asts.Ast):
    def __eq__(self, other: ConventionMovAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, ConventionMovAst)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return ""

    @property
    def pos_end(self) -> int:
        return self.pos


__all__ = [
    "ConventionMovAst"]
