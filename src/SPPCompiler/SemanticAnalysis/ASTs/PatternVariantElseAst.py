from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class PatternVariantElseAst(Ast):
    tok_else: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwElse))

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_else.print(printer)


__all__ = ["PatternVariantElseAst"]
