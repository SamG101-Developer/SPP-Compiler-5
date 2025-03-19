from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantElseAst(Ast):
    tok_else: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwElse))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_else.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_else.pos_end

    def analyse_semantics(self, scope_manager: ScopeManager, condition: Asts.ExpressionAst = None, **kwargs) -> None:
        # Modified signature to include a condition, uniform with other "PatternXXXAst" types.
        ...


__all__ = ["PatternVariantElseAst"]
