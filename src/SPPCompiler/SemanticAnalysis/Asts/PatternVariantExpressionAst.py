from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class PatternVariantExpressionAst(Asts.Ast):
    expr: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.expr is not None

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
        AstMemoryUtils.enforce_memory_integrity(self.expr, self.expr, sm)


__all__ = [
    "PatternVariantExpressionAst"]
