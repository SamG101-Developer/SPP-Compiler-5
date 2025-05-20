from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy


@dataclass(slots=True)
class GenericTypeArgumentUnnamedAst(Asts.Ast, Asts.Mixins.OrderableAst):
    value: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self._variant = "Unnamed"

    def __eq__(self, other: GenericTypeArgumentUnnamedAst) -> bool:
        return other.__class__ is GenericTypeArgumentUnnamedAst and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __deepcopy__(self, memodict=None) -> GenericTypeArgumentUnnamedAst:
        # Create a deep copy of the AST.
        return GenericTypeArgumentUnnamedAst(pos=self.pos, value=fast_deepcopy(self.value))

    def __str__(self) -> str:
        return str(self.value)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.value.print(printer)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the value of the generic type argument.
        convention = self.value.convention
        self.value.analyse_semantics(sm, **kwargs)
        self.value = sm.current_scope.get_symbol(self.value).fq_name.with_convention(convention)


__all__ = [
    "GenericTypeArgumentUnnamedAst"]
