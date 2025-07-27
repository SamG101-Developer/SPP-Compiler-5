from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True, repr=False)
class ConventionRefAst(Asts.Ast):
    tok_borrow: Asts.TokenAst = field(default=None)

    def __eq__(self, other: ConventionRefAst) -> bool:
        # Check both ASTs are the same type.
        return type(other) is ConventionRefAst

    def __hash__(self) -> int:
        # Hash the AST.
        return 2

    def __str__(self) -> str:
        # String representation of the AST.
        return "&"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return "&"

    @property
    def pos_end(self) -> int:
        return self.tok_borrow.pos_end


__all__ = [
    "ConventionRefAst"]
