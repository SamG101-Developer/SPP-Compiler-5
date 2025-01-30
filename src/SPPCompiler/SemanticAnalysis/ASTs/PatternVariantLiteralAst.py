from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantLiteralAst(Ast, PatternMapping):
    literal: Asts.LiteralAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.literal

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.literal.print(printer)

    @std.override_method
    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableSingleIdentifierAst:
        # Convert the dummy single identifier into a local variable single identifier.
        return Asts.LocalVariableSingleIdentifierAst(pos=self.pos, name=Asts.IdentifierAst(self.pos, f"$l{id(self)}"))

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, condition: Asts.ExpressionAst = None, **kwargs) -> None:
        # Analyse the literal.
        self.literal.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantLiteralAst"]
