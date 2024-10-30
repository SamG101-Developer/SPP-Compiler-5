from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.CaseExpressionAst import CaseExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantElseCaseAst(Ast, Stage4_SemanticAnalyser):
    tok_else: TokenAst
    case_expression: CaseExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_else.print(printer) + " ",
            self.case_expression.print(printer)]
        return "".join(string)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the case expression.
        self.case_expression.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantElseCaseAst"]
