from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True, repr=False)
class LambdaExpressionCaptureItemAst(Asts.Ast, Asts.Mixins.OrderableAst):
    """
    The LambdaExpressionCaptureItemAst class represents a capture item in a lambda expression. A convention can be
    applied to the capture, which determines the lambda's function type: the most restrictive capture is used to
    determine the function type. If there is a "move" capture, then the lambda is a "FunMov" type.
    """

    convention: Optional[Asts.ConventionAst] = field(default=None)
    """The convention applied to the borrow from the outer context."""

    value: Asts.IdentifierAst = field(default=None)
    """The identifier of the capture item (variable name)."""

    def __post_init__(self) -> None:
        self._variant = "Unnamed"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return "".join([self.convention.print(printer) if self.convention else "", self.value.print(printer)])

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self.value.analyse_semantics(sm, **kwargs)


__all__ = [
    "LambdaExpressionCaptureItemAst",
]
