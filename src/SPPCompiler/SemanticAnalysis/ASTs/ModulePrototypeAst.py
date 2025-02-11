from __future__ import annotations

import functools
import os
from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ModulePrototypeAst(Ast):
    body: Asts.ModuleImplementationAst = field(default_factory=Asts.ModuleImplementationAst)
    _name: str = field(init=False, default="")

    @ast_printer_method
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

    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the module implementation.
        super().pre_process(context)
        self.body.pre_process(context)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Generate the module symbol.
        super().generate_top_level_scopes(scope_manager)
        self.body.generate_top_level_scopes(scope_manager)

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Alias the types in the module implementation.
        self.body.generate_top_level_aliases(scope_manager, **kwargs)

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes.
        self.body.load_super_scopes(scope_manager)

    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        # Alias the types in the module implementation.
        self.body.regenerate_generic_aliases(scope_manager)

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Regenerate the generic types in the module implementation.
        self.body.regenerate_generic_types(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the module implementation.
        self.body.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ModulePrototypeAst"]
