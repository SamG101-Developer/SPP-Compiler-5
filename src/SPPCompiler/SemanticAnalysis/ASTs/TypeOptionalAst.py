from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class TypeOptionalAst(Ast):
    tok_qst: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkQst))
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.type

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return f""

    def to_type(self) -> Asts.TypeAst:
        return CommonTypes.Opt(self.type, self.type.pos)


__all__ = ["TypeOptionalAst"]
