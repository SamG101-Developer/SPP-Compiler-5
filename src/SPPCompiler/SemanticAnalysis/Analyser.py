from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree
    from SPPCompiler.SemanticAnalysis.ASTs.ProgramAst import ProgramAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class Analyser:
    _ast: ProgramAst
    _scope_manager: Optional[ScopeManager]

    def __init__(self, ast: ProgramAst) -> None:
        self._ast = ast
        self._scope_manager = None

    def analyse(self, module_tree: ModuleTree) -> None:
        from SPPCompiler.Utils.Errors import SemanticError
        from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

        self._scope_manager = ScopeManager()

        try:
            self._ast.pre_process(None)
            self._ast.generate_symbols(self._scope_manager, module_tree)
        except SemanticError as error:
            errored_module = module_tree.modules.find(lambda module: self._ast.current() == module.module_ast)
            error.throw(errored_module.error_formatter)
