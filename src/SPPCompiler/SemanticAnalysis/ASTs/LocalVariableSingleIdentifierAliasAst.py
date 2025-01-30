from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class LocalVariableSingleIdentifierAliasAst(Ast):
    tok_as: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwAs))
    name: Asts.IdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_as.print(printer) + " ",
            self.name.print(printer)]
        return "".join(string)


__all__ = ["LocalVariableSingleIdentifierAliasAst"]
