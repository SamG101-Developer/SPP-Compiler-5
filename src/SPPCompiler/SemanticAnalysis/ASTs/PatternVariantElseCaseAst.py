from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantElseCaseAst(Ast):
    tok_else: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwElse))
    case_expression: Asts.CaseExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.case_expression

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_else.print(printer) + " ",
            self.case_expression.print(printer)]
        return "".join(string)

    def analyse_semantics(self, scope_manager: ScopeManager, condition: Asts.ExpressionAst = None, **kwargs) -> None:
        # Analyse the case expression.
        self.case_expression.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantElseCaseAst"]
