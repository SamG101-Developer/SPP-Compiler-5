from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True, repr=False)
class ConventionMutAst(Asts.Ast):
    tok_borrow: Asts.TokenAst = field(default=None)
    tok_mut: Asts.TokenAst = field(default=None)

    def __eq__(self, other: ConventionMutAst) -> bool:
        # Check both ASTs are the same type.
        return type(other) is ConventionMutAst

    def __hash__(self) -> int:
        # Hash the AST.
        return 1

    def __str__(self) -> str:
        # String representation of the AST.
        return "&mut "

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return "&mut "

    @property
    def pos_end(self) -> int:
        return self.tok_mut.pos_end


__all__ = [
    "ConventionMutAst"]
