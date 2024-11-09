from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericTypeArgumentUnnamedAst(Ast, Ordered, Stage4_SemanticAnalyser):
    value: TypeAst

    def __post_init__(self) -> None:
        self._variant = "Unnamed"

    def __eq__(self, other: GenericTypeArgumentUnnamedAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return isinstance(other, GenericTypeArgumentUnnamedAst) and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the value of the generic type argument.
        self.value.analyse_semantics(scope_manager, **kwargs)
        self.value = scope_manager.current_scope.get_symbol(self.value).fq_name


__all__ = ["GenericTypeArgumentUnnamedAst"]
