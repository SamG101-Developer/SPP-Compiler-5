from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericTypeArgumentUnnamedAst(Ast, Ordered):
    value: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        # assert self.value
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

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the value of the generic type argument.
        convention = self.value.get_convention()
        self.value.analyse_semantics(scope_manager, **kwargs)
        self.value = scope_manager.current_scope.get_symbol(self.value).fq_name.with_convention(convention)

        if type(convention) is not Asts.ConventionMovAst:
            self.value = self.value.with_convention(convention)


__all__ = ["GenericTypeArgumentUnnamedAst"]
