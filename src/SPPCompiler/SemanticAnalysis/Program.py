from __future__ import annotations

import os.path
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.ProgressBar import ProgressBar
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree, Module
    from SPPCompiler.SemanticAnalysis.ASTs.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class Program(CompilerStages):
    modules: Seq[ModulePrototypeAst] = field(default_factory=Seq, init=False, repr=False)
    _current: Optional[ModulePrototypeAst] = field(default=None, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return ""

    def pre_process(self, context: PreProcessingContext, progress_bar: ProgressBar = None, module_tree: ModuleTree = None) -> None:
        # Pre-process all the modules.
        for module in self.modules:
            module_in_tree = module_tree.modules.find(lambda m: m.module_ast is module)
            module._name = module_in_tree.path
            progress_bar.next(module.name.value)
            self._current = module
            module.pre_process(module)

    def generate_symbols(self, scope_manager: ScopeManager, progress_bar: ProgressBar = None, module_tree: ModuleTree = None) -> None:
        # Generate symbols for all the modules, including namespaces in the scope manager.
        for module in self.modules:
            progress_bar.next(module.name.value)
            self._move_scope_manager_to_namespace(scope_manager, module_tree.modules.find(lambda m: m.module_ast is module))
            self._current = module
            module.generate_symbols(scope_manager)
            scope_manager.reset()

    def alias_types(self, scope_manager: ScopeManager, progress_bar: ProgressBar = None, **kwargs) -> None:
        # Alias types for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            self._current = module
            module.alias_types(scope_manager, **kwargs)
        scope_manager.reset()

    def load_sup_scopes(self, scope_manager: ScopeManager, progress_bar: ProgressBar = None) -> None:
        # Load the super scopes for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            self._current = module
            module.load_sup_scopes(scope_manager)
        scope_manager.reset()

    def inject_sup_scopes(self, scope_manager: ScopeManager, progress_bar: ProgressBar = None) -> None:
        # Inject the super scopes for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            self._current = module
            module.inject_sup_scopes(scope_manager)
        scope_manager.reset()

        # Prune the generic scopes of the scope tree.
        # Todo: move into scope class
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol, AliasSymbol
        for scope in scope_manager:
            for symbol in scope.all_symbols(exclusive=True).filter_to_type(TypeSymbol, AliasSymbol).filter(lambda t: not t.is_generic):
                if symbol.name.generic_argument_group.arguments and symbol.scope._non_generic_scope is not symbol.scope:
                    scope.rem_symbol(symbol.name)
        scope_manager.reset()

    def alias_types_regeneration(self, scope_manager: ScopeManager, progress_bar: ProgressBar = None) -> None:
        # Generate generic types for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            self._current = module
            module.alias_types_regeneration(scope_manager)
        scope_manager.reset()

    def regenerate_generic_types(self, scope_manager: ScopeManager, progress_bar: ProgressBar = None) -> None:
        # Regenerate generic types for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            self._current = module
            module.regenerate_generic_types(scope_manager)
        scope_manager.reset()

    def analyse_semantics(self, scope_manager: ScopeManager, progress_bar: ProgressBar = None, **kwargs) -> None:
        # Analyse the semantics for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            self._current = module
            module.analyse_semantics(scope_manager, **kwargs)
        scope_manager.reset()

    def current(self) -> ModulePrototypeAst:
        return self._current

    def _move_scope_manager_to_namespace(self, scope_manager: ScopeManager, module: Module):
        from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        module_namespace = module.path.split(os.path.sep)
        module_namespace = module_namespace[module_namespace.index("src") + 1 : -1]

        for part in module_namespace:
            part = IdentifierAst(-1, part)

            if Seq(scope_manager.current_scope.children).map(lambda s: s.name).contains(part):
                scope = Seq(scope_manager.current_scope.children).filter(lambda s: s.name == part).first()
                if scope_manager.current_scope is not scope: scope_manager.reset(scope)

            else:
                scope_manager.current_scope.add_symbol(namespace_symbol := NamespaceSymbol(name=part))
                scope = scope_manager.create_and_move_into_new_scope(part)
                namespace_symbol.scope = scope
                namespace_symbol.scope._type_symbol = namespace_symbol
                namespace_symbol.scope._ast = module.module_ast


__all__ = ["Program"]
