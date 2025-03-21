from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class WhereConstraintsGroupAst(Ast):
    tok_left_brack: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftSquareBracket))
    constraints: Seq[Asts.WhereConstraintsAst] = field(default_factory=Seq)
    tok_right_brack: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightSquareBracket))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_brack.print(printer),
            self.constraints.print(printer, ", "),
            self.tok_right_brack.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_right_brack.pos_end


__all__ = ["WhereConstraintsGroupAst"]
