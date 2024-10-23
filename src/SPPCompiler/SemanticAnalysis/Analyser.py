from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree
    from SPPCompiler.SemanticAnalysis.ASTs.ProgramAst import ProgramAst


class Analyser:
    _ast: ProgramAst

    def __init__(self, ast: ProgramAst) -> None:
        self._ast = ast

    def analyse(self, module_tree: ModuleTree) -> None:
        from SPPCompiler.Utils.Errors import SemanticError

        try:
            self._ast.pre_process(None)
        except SemanticError as error:
            errored_module = module_tree.modules.find(lambda module: self._ast.current() == module.module_ast)
            error.throw(errored_module.error_formatter)
