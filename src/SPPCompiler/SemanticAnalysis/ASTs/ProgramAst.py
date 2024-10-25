from __future__ import annotations

import os.path
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree, Module
    from SPPCompiler.SemanticAnalysis.ASTs.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ProgramAst(Ast, Stage1_PreProcessor, Stage2_SymbolGenerator):
    modules: Seq[ModulePrototypeAst]
    _current: Optional[ModulePrototypeAst] = field(default=None, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return ""

    def pre_process(self, context: PreProcessingContext) -> None:
        for module in self.modules:
            self._current = module
            module.body.members.for_each(lambda m: m.pre_process(module))

    def generate_symbols(self, scope_manager: ScopeManager, module_tree: Optional[ModuleTree] = None) -> None:
        for module in self.modules:
            self._move_scope_manager_to_namespace(scope_manager, module_tree.modules.find(lambda m: m.module_ast == module))
            self._current = module
            module.body.members.for_each(lambda m: m.generate_symbols(scope_manager))
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
                scope_manager.reset(scope)

            else:
                scope_manager.current_scope.add_symbol(namespace_symbol := NamespaceSymbol(name=part))
                scope = scope_manager.create_and_move_into_new_scope(part)
                namespace_symbol.scope = scope


__all__ = ["ProgramAst"]
