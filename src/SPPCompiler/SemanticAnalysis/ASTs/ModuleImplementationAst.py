from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ModuleMemberAst import ModuleMemberAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ModuleImplementationAst(Ast, CompilerStages):
    members: Seq[ModuleMemberAst]

    def __post_init__(self) -> None:
        # Convert the members into a sequence.
        self.members = Seq(self.members)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.members.print(printer, "\n")

    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the members.
        for m in self.members: m.pre_process(context)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Generate the symbols for the members.
        for m in self.members: m.generate_symbols(scope_manager)

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Alias the types in the members.
        for m in self.members: m.alias_types(scope_manager, **kwargs)

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes.
        for m in self.members: m.load_sup_scopes(scope_manager)

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Inject the super scopes.
        for m in self.members: m.inject_sup_scopes(scope_manager)

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        # Alias the types in the members for regeneration.
        for m in self.members: m.alias_types_regeneration(scope_manager)

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Regenerate the generic types in the members.
        for m in self.members: m.regenerate_generic_types(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the members.
        for m in self.members: m.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ModuleImplementationAst"]
