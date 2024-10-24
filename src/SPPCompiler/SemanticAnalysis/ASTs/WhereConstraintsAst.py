from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class WhereConstraintsAst(Ast):
    types: Seq[TypeAst]
    tok_colon: TokenAst
    constraints: Seq[TypeAst]

    def __post_init__(self) -> None:
        # Convert the types and constraints into a sequence.
        self.types = Seq(self.types)
        self.constraints = Seq(self.constraints)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.types.print(printer, ", "),
            self.tok_colon.print(printer),
            self.constraints.print(printer, ", ")]
        return " ".join(string)


__all__ = ["WhereConstraintsAst"]
