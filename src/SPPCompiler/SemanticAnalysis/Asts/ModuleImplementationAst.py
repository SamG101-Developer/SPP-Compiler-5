from __future__ import annotations

from dataclasses import dataclass, field

from llvmlite import ir

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class ModuleImplementationAst(Asts.Ast):
    members: list[Asts.ModuleMemberAst] = field(default_factory=list)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return SequenceUtils.print(printer, self.members, sep="\n")

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

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        # Qualify the types in the members.
        for m in self.members: m.qualify_types(sm, **kwargs)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Load the super scopes.
        for m in self.members: m.load_super_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Pre analyse the members
        for m in self.members: m.pre_analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the members.
        for m in self.members: m.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Check the memory for the members.
        for m in self.members: m.check_memory(sm, **kwargs)

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        # Generate the code for the members.
        for m in self.members: m.code_gen_pass_1(sm, llvm_module, **kwargs)

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        # Generate the code for the members.
        for m in self.members: m.code_gen_pass_2(sm, llvm_module, **kwargs)


__all__ = [
    "ModuleImplementationAst"]
