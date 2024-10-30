from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantExpressionAst(Ast, Stage4_SemanticAnalyser):
    expression: ExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.expression.print(printer)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expression, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.expression)

        # Analyse the expression and enforce memory integrity.
        self.expression.analyse_semantics(scope_manager, **kwargs)
        AstMemoryHandler.enforce_memory_integrity(self.expression, self.expression, scope_manager)


__all__ = ["PatternVariantExpressionAst"]
