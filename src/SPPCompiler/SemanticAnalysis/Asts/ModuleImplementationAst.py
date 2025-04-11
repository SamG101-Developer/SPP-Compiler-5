from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ModuleImplementationAst(Asts.Ast):
    members: Seq[Asts.ModuleMemberAst] = field(default_factory=Seq)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.members.print(printer, "\n")

    @property
    def pos_end(self) -> int:
        return self.members[-1].pos_end if self.members else self.pos

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the members.
        for m in self.members: m.pre_process(ctx)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Generate the symbols for the members.
        for m in self.members: m.generate_top_level_scopes(sm)

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Alias the types in the members.
        for m in self.members: m.generate_top_level_aliases(sm, **kwargs)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Load the super scopes.
        for m in self.members: m.load_super_scopes(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the members.
        for m in self.members: m.analyse_semantics(sm, **kwargs)


__all__ = [
    "ModuleImplementationAst"]
