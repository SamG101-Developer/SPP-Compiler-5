from __future__ import annotations

import os.path
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.Lexer import Lexer
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import CompilerStages, PreProcessingContext
from SPPCompiler.SyntacticAnalysis.ErrorFormatter import ErrorFormatter
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.ProgressBar import ProgressBar
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.Compiler.ModuleTree import ModuleTree, Module
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class Program(CompilerStages):
    modules: Seq[Asts.ModulePrototypeAst] = field(default_factory=Seq, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return ""

    def lex(self, progress_bar: Optional[ProgressBar] = None, module_tree: ModuleTree = None) -> None:
        # Lexing stage.
        for module in module_tree:
            with open(os.path.join(os.getcwd(), module.path.lstrip(os.path.sep))) as fo:
                module.code = fo.read()
            module.token_stream = Lexer(module.code).lex()
            progress_bar.next(module.path)
            module.error_formatter = ErrorFormatter(module.token_stream, module.path)

    def parse(self, progress_bar: Optional[ProgressBar] = None, module_tree: ModuleTree = None) -> None:
        # Parsing stage.
        for module in module_tree:
            module.module_ast = SppParser(module.token_stream, module.path, module.error_formatter).parse()
            progress_bar.next(module.path)

            # Remove vcs "main.spp" files.
            module_namespace = module.path.split(os.path.sep)
            module_namespace = module_namespace[module_namespace.index("src") + 1: -1]
            if module.path.startswith(os.path.sep + "vcs") and not module_namespace:
                module_tree.modules.remove(module)

    def pre_process(self, context: PreProcessingContext, progress_bar: Optional[ProgressBar] = None, module_tree: ModuleTree = None) -> None:
        # Pre-process all the modules.
        for module in self.modules:
            module_in_tree = module_tree.modules.find(lambda m: m.module_ast is module)
            module._name = module_in_tree.path
            progress_bar.next(module.name.value)
            module.pre_process(module)
        progress_bar.finish()

    def generate_top_level_scopes(self, sm: ScopeManager, progress_bar: Optional[ProgressBar] = None, module_tree: ModuleTree = None) -> None:
        # Generate symbols for all the modules, including namespaces in the scope manager.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, module_tree.modules.find(lambda m: m.module_ast is module))
            progress_bar.next(module.name.value)
            module.generate_top_level_scopes(sm)
            sm.reset()
        progress_bar.finish()

    def generate_top_level_aliases(self, sm: ScopeManager, progress_bar: Optional[ProgressBar] = None, **kwargs) -> None:
        # Alias types for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            module.generate_top_level_aliases(sm, **kwargs)
        progress_bar.finish()
        sm.reset()

    def load_super_scopes(self, sm: ScopeManager, progress_bar: Optional[ProgressBar] = None) -> None:
        # Load the super scopes for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            module.load_super_scopes(sm)
        progress_bar.finish()
        sm.reset()
        sm.relink_generics()

    def analyse_semantics(self, sm: ScopeManager, progress_bar: Optional[ProgressBar] = None, **kwargs) -> None:
        # Analyse the semantics for all the modules.
        for module in self.modules:
            progress_bar.next(module.name.value)
            module.analyse_semantics(sm, **kwargs)
        progress_bar.finish()
        sm.reset()

    def _move_scope_manager_to_namespace(self, sm: ScopeManager, module: Module):
        from SPPCompiler.SemanticAnalysis import Asts
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        module_namespace = module.path.split(os.path.sep)
        module_namespace = module_namespace[module_namespace.index("src") + 1:]
        module_namespace[-1] = module_namespace[-1].split(".")[0]

        for part in module_namespace:
            part = Asts.IdentifierAst(-1, part)

            if Seq(sm.current_scope.children).map(lambda s: s.name).contains(part):
                scope = Seq(sm.current_scope.children).filter(lambda s: s.name == part).first()
                if sm.current_scope is not scope: sm.reset(scope)

            else:
                sm.current_scope.add_symbol(namespace_symbol := NamespaceSymbol(name=part))
                scope = sm.create_and_move_into_new_scope(part, error_formatter=module.error_formatter)
                namespace_symbol.scope = scope
                namespace_symbol.scope._type_symbol = namespace_symbol
                namespace_symbol.scope._ast = module.module_ast


__all__ = ["Program"]
