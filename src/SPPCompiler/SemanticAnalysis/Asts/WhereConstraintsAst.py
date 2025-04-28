from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
class WhereConstraintsAst(Asts.Ast):
    types: Seq[Asts.TypeAst] = field(default_factory=Seq)
    tok_colon: Asts.TokenAst = field(default=None)
    constraints: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        assert self.constraints is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.types, sep=", "),
            self.tok_colon.print(printer),
            self.constraints.print(printer, ", ")]
        return " ".join(string)

    @property
    def pos_end(self) -> int:
        return self.constraints.pos_end


__all__ = [
    "WhereConstraintsAst"]
