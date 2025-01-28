from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class ConventionRefAst(Ast):
    tok_borrow: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBorrow))

    @std.override_method
    def __eq__(self, other: ConventionRefAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, ConventionRefAst)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_borrow.print(printer)


__all__ = ["ConventionRefAst"]
