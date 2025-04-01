from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class GenericTypeArgumentUnnamedAst(Asts.Ast, Asts.Mixins.OrderableAst):
    value: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self._variant = "Unnamed"

    def __eq__(self, other: GenericTypeArgumentUnnamedAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return isinstance(other, GenericTypeArgumentUnnamedAst) and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the value of the generic type argument.
        convention = self.value.get_conventions()
        self.value.analyse_semantics(sm, **kwargs)
        self.value = sm.current_scope.get_symbol(self.value).fq_name.with_conventions(convention)


__all__ = [
    "GenericTypeArgumentUnnamedAst"]
