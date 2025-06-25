from __future__ import annotations

from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True)
class IterExpressionBranchAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    Represents a branch in an iteration expression, which will contain a pattern and an inner scope.
    """

    pattern: Asts.IterPatternAst = None
    """The pattern that this branch matches."""

    inner_scope: Asts.InnerScopeAst = None
    """The inner scope that this branch executes if the pattern matches."""

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.pattern.print(printer)}{self.inner_scope.print(printer)}"

    def __str__(self) -> str:
        return f"{self.pattern}{self.inner_scope}"

    @property
    def pos_end(self) -> int:
        return self.inner_scope.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        return self.inner_scope.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        self.pattern.analyse_semantics(sm, cond=cond, **kwargs)
        self.inner_scope.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self.pattern.check_memory(sm, **kwargs)
        self.inner_scope.check_memory(sm, **kwargs)


__all__ = ["IterExpressionBranchAst"]
