from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class WhereConstraintsAst(Ast):
    types: Seq[Asts.TypeAst] = field(default_factory=Seq)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    constraints: Asts.TypeAst = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.types.print(printer, ", "),
            self.tok_colon.print(printer),
            self.constraints.print(printer, ", ")]
        return " ".join(string)

    @property
    def pos_end(self) -> int:
        return self.constraints.pos_end


__all__ = ["WhereConstraintsAst"]
