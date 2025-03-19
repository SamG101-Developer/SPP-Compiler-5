from __future__ import annotations

from dataclasses import dataclass, field


import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ModuleImplementationAst(Ast):
    members: Seq[Asts.ModuleMemberAst] = field(default_factory=Seq)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.members.print(printer, "\n")

    @property
    def pos_end(self) -> int:
        return self.members[-1].pos_end

    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the members.
        for m in self.members: m.pre_process(context)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Generate the symbols for the members.
        for m in self.members: m.generate_top_level_scopes(scope_manager)

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Alias the types in the members.
        for m in self.members: m.generate_top_level_aliases(scope_manager, **kwargs)

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes.
        for m in self.members: m.load_super_scopes(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the members.
        for m in self.members: m.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ModuleImplementationAst"]
