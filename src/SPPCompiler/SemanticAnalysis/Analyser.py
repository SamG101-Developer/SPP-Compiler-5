from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree
    from SPPCompiler.SemanticAnalysis.ASTs.ProgramAst import ProgramAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


def create_global() -> Scope:
    from SPPCompiler.SemanticAnalysis import IdentifierAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

    # Create a new global scope.
    global_scope = Scope(name=IdentifierAst(-1, "_global"))

    # Inject the "_global" namespace symbol into this scope (makes lookups orthogonal).
    global_namespace_symbol = NamespaceSymbol(name=global_scope.name, scope=global_scope)
    global_scope.add_symbol(global_namespace_symbol)
    global_scope._type_symbol = global_namespace_symbol

    # Return the global scope.
    return global_scope


class Analyser:
    _ast: ProgramAst
    _scope_manager: Optional[ScopeManager]

    def __init__(self, ast: ProgramAst) -> None:
        self._ast = ast
        self._scope_manager = None

    def analyse(self, module_tree: ModuleTree) -> None:
        from SPPCompiler.Utils.Errors import SemanticError
        from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

        self._scope_manager = ScopeManager(global_scope=create_global())

        try:
            self._ast.pre_process(None)
            self._ast.generate_symbols(self._scope_manager, module_tree)
            self._ast.load_sup_scopes(self._scope_manager)
            self._ast.analyse_semantics(self._scope_manager)
        except SemanticError as error:
            errored_module = module_tree.modules.find(lambda module: self._ast.current() == module.module_ast)
            error.throw(errored_module.error_formatter)
