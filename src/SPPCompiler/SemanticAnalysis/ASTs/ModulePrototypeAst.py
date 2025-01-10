from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import functools, os

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.ModuleImplementationAst import ModuleImplementationAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ModulePrototypeAst(Ast, CompilerStages):
    body: ModuleImplementationAst
    _name: str = field(init=False, default="")

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.body.print(printer)

    @functools.cached_property
    def name(self) -> IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst

        parts = self._name.split(os.path.sep)
        parts = parts[parts.index("src") + 1 :]
        name = "::".join(parts)
        return IdentifierAst(self.pos, name)

    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the module implementation.
        super().pre_process(context)
        self.body.pre_process(context)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Generate the module symbol.
        super().generate_symbols(scope_manager)
        self.body.generate_symbols(scope_manager)

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Alias the types in the module implementation.
        self.body.alias_types(scope_manager, **kwargs)

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes.
        self.body.load_sup_scopes(scope_manager)

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Inject the super scopes.
        self.body.inject_sup_scopes(scope_manager)

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        # Alias the types in the module implementation.
        self.body.alias_types_regeneration(scope_manager)

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Regenerate the generic types in the module implementation.
        self.body.regenerate_generic_types(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the module implementation.
        self.body.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ModulePrototypeAst"]
