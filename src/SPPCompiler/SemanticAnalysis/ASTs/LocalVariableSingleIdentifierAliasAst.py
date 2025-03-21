from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class LocalVariableSingleIdentifierAliasAst(Ast):
    tok_as: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwAs))
    name: Asts.IdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_as.print(printer) + " ",
            self.name.print(printer)]
        return "".join(string)


__all__ = ["LocalVariableSingleIdentifierAliasAst"]
