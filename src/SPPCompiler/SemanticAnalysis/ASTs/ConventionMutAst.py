from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class ConventionMutAst(Ast):
    tok_borrow: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBorrow))
    tok_mut: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwMut))

    @std.override_method
    def __eq__(self, other: ConventionMutAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, ConventionMutAst)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_borrow.print(printer),
            self.tok_mut.print(printer) + " "]
        return "".join(string)


__all__ = ["ConventionMutAst"]
