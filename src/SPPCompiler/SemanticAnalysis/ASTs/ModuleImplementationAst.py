from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ModuleImplementationAst(Ast, CompilerStages):
    members: Seq[Asts.ModuleMemberAst] = field(default_factory=Seq)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.members.print(printer, "\n")

    @std.override_method
    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the members.
        for m in self.members: m.pre_process(context)

    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Generate the symbols for the members.
        for m in self.members: m.generate_top_level_scopes(scope_manager)

    @std.override_method
    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Alias the types in the members.
        for m in self.members: m.generate_top_level_aliases(scope_manager, **kwargs)

    @std.override_method
    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes.
        for m in self.members: m.load_super_scopes(scope_manager)

    @std.override_method
    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Inject the super scopes.
        for m in self.members: m.postprocess_super_scopes(scope_manager)

    @std.override_method
    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        # Alias the types in the members for regeneration.
        for m in self.members: m.regenerate_generic_aliases(scope_manager)

    @std.override_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Regenerate the generic types in the members.
        for m in self.members: m.regenerate_generic_types(scope_manager)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the members.
        for m in self.members: m.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ModuleImplementationAst"]
