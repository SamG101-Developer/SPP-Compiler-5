from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import functools, os, std

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ModulePrototypeAst(Ast, CompilerStages):
    body: Asts.ModuleImplementationAst = field(default_factory=Asts.ModuleImplementationAst)
    _name: str = field(init=False, default="")

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.body.print(printer)

    @functools.cached_property
    def name(self) -> Asts.IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst

        parts = self._name.split(os.path.sep)
        parts = parts[parts.index("src") + 1 :]
        name = "::".join(parts)
        return IdentifierAst(self.pos, name)

    @std.override_method
    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the module implementation.
        super().pre_process(context)
        self.body.pre_process(context)

    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Generate the module symbol.
        super().generate_top_level_scopes(scope_manager)
        self.body.generate_top_level_scopes(scope_manager)

    @std.override_method
    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Alias the types in the module implementation.
        self.body.generate_top_level_aliases(scope_manager, **kwargs)

    @std.override_method
    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes.
        self.body.load_super_scopes(scope_manager)

    @std.override_method
    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Inject the super scopes.
        self.body.postprocess_super_scopes(scope_manager)

    @std.override_method
    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        # Alias the types in the module implementation.
        self.body.regenerate_generic_aliases(scope_manager)

    @std.override_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Regenerate the generic types in the module implementation.
        self.body.regenerate_generic_types(scope_manager)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the module implementation.
        self.body.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ModulePrototypeAst"]
