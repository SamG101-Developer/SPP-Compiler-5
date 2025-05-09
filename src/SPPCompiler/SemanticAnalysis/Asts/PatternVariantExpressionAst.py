from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class PatternVariantExpressionAst(Asts.Ast):
    expr: Asts.ExpressionAst = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.expr.print(printer)

    @property
    def pos_end(self) -> int:
        return self.expr.pos_end

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expr, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.expr)

        # Analyse the expression and enforce memory integrity.
        self.expr.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self.expr.check_memory(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(
            self.expr, self.expr, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
            check_pins=True, mark_moves=True)


__all__ = [
    "PatternVariantExpressionAst"]
