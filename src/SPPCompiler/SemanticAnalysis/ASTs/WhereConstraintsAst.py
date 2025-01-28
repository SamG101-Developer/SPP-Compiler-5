from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class WhereConstraintsAst(Ast):
    types: Seq[Asts.TypeAst] = field(default_factory=Seq)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkColon))
    constraints: Seq[Asts.TypeAst] = field(default_factory=Seq)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.types.print(printer, ", "),
            self.tok_colon.print(printer),
            self.constraints.print(printer, ", ")]
        return " ".join(string)


__all__ = ["WhereConstraintsAst"]
