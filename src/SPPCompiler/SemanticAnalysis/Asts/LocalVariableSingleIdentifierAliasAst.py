from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True)
class LocalVariableSingleIdentifierAliasAst(Asts.Ast):
    kw_as: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwAs))
    name: Asts.IdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_as = self.kw_as or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwAs)
        assert self.name is not None

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_as.print(printer) + " ",
            self.name.print(printer)]
        return "".join(string)


__all__ = [
    "LocalVariableSingleIdentifierAliasAst"]
