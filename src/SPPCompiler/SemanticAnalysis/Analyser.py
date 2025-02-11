from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree, Module
    from SPPCompiler.Compiler.Program import Program
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


def create_global(module: Module) -> Scope:
    from SPPCompiler.SemanticAnalysis import IdentifierAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

    # Create a new global scope.
    global_scope = Scope(name=IdentifierAst(-1, "_global"))

    # Inject the "_global" namespace symbol into this scope (makes lookups orthogonal).
    global_namespace_symbol = NamespaceSymbol(name=global_scope.name, scope=global_scope)
    global_scope.add_symbol(global_namespace_symbol)
    global_scope._type_symbol = global_namespace_symbol
    global_scope._ast = module.module_ast

    # Return the global scope.
    return global_scope


class Analyser:
    _ast: Program
    _scope_manager: Optional[ScopeManager]

    def __init__(self, ast: Program) -> None:
        self._ast = ast
        self._scope_manager = None

    def analyse(self, module_tree: ModuleTree) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticError
        from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
        from SPPCompiler.Utils.ProgressBar import ProgressBar

        self._scope_manager = ScopeManager(global_scope=create_global(module_tree.modules[0]))

        progress_bars = [
            ProgressBar("Pre-processing.................", module_tree.modules.length),
            ProgressBar("Generating top-level scopes....", module_tree.modules.length),
            ProgressBar("Generating top-level aliases...", module_tree.modules.length),
            ProgressBar("Loading super scopes...........", module_tree.modules.length),
            ProgressBar("Regenerating generic aliases...", module_tree.modules.length),
            ProgressBar("Regenerating generic types.....", module_tree.modules.length),
            ProgressBar("Analysing semantics............", module_tree.modules.length)]

        try:
            self._ast.pre_process(None, progress_bars[0], module_tree)
            self._ast.generate_top_level_scopes(self._scope_manager, progress_bars[1], module_tree)
            self._ast.generate_top_level_aliases(self._scope_manager, progress_bars[2])
            self._ast.load_super_scopes(self._scope_manager, progress_bars[3])
            self._ast.regenerate_generic_aliases(self._scope_manager, progress_bars[4])
            self._ast.regenerate_generic_types(self._scope_manager, progress_bars[5])
            self._ast.analyse_semantics(self._scope_manager, progress_bars[6])

        except SemanticError as error:
            errored_module = module_tree.modules.find(lambda module: self._ast.current() is module.module_ast)
            error.throw(errored_module.error_formatter)
