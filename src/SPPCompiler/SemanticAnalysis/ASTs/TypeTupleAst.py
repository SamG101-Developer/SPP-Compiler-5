from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeTupleAst(Ast):
    tok_left_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenL))
    elements: Seq[Asts.TypeAst] = field(default_factory=Seq)
    tok_right_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenR))

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return ""

    def to_type(self) -> Asts.TypeAst:
        return CommonTypes.Tup(self.elements, self.tok_left_paren.pos)


__all__ = ["TypeTupleAst"]
