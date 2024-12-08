from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableSingleIdentifierAst import LocalVariableSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LiteralAst import LiteralAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantLiteralAst(Ast, PatternMapping, CompilerStages):
    literal: LiteralAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.literal.print(printer)

    def convert_to_variable(self, **kwargs) -> LocalVariableSingleIdentifierAst:
        # Convert the dummy single identifier into a local variable single identifier.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, LocalVariableSingleIdentifierAst
        return LocalVariableSingleIdentifierAst(self.pos, None, IdentifierAst(self.pos, f"$l{id(self)}"))

    def analyse_semantics(self, scope_manager: ScopeManager, condition: ExpressionAst = None, **kwargs) -> None:
        # Analyse the literal.
        self.literal.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantLiteralAst"]
