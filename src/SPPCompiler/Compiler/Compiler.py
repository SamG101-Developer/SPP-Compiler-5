from __future__ import annotations

import hashlib
import json
import os
from typing import TYPE_CHECKING, Optional

from fastenum import Enum

from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticError
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree
    from SPPCompiler.Compiler.Program import Program

COMPILER_STAGE_NAMES = [
    "            Lexing",
    "           Parsing",
    "    Pre-processing",
    "  Top-level scopes",
    " Top-level aliases",
    "      Super scopes",
    "Semantics analysis"]


class Compiler:
    class Mode(Enum):
        Dev = "d"
        Rel = "r"

    _src_path: str
    _module_tree: ModuleTree
    _mode: Mode
    _ast: Program
    _scope_manager: Optional[ScopeManager]

    def __init__(self, mode: Mode) -> None:
        from SPPCompiler.Compiler.ModuleTree import ModuleTree
        from SPPCompiler.Compiler.Program import Program

        # Register the parameters against the instance.
        self._src_path = os.path.join(os.getcwd(), "src")
        self._module_tree = ModuleTree(os.getcwd())
        self._mode = mode
        self._ast = Program()

        # Compile the modules.
        self.compile()

    def compile(self) -> None:
        from SPPCompiler.LexicalAnalysis.Lexer import SppLexer
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypesPrecompiled
        from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter
        from SPPCompiler.SyntacticAnalysis.ErrorFormatter import ErrorFormatter
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser
        from SPPCompiler.Utils.ProgressBar import ProgressBar

        progress_bars = [ProgressBar(name, self._module_tree.modules.length) for name in COMPILER_STAGE_NAMES]

        # Lexing stage.
        for module in self._module_tree.modules:
            with open(os.path.join(os.getcwd(), module.path.lstrip(os.path.sep))) as fo:
                module.code = fo.read()
            module.token_stream = SppLexer(module.code).lex()
            progress_bars[0].next(module.path)
            module.error_formatter = ErrorFormatter(module.token_stream, module.path)

        # Parsing stage.
        for module in self._module_tree.modules.copy():
            module.module_ast = SppParser(module.token_stream, module.path, module.error_formatter).parse()
            progress_bars[1].next(module.path)

            # Remove vcs "main.spp" files.
            module_namespace = module.path.split(os.path.sep)
            module_namespace = module_namespace[module_namespace.index("src") + 1: -1]
            if module.path.startswith(os.path.sep + "vcs") and not module_namespace:
                self._module_tree.modules.remove(module)
        CommonTypesPrecompiled.initialize()

        # Save the modules into the ProgramAst
        self._ast.modules = Seq([module.module_ast for module in self._module_tree.modules])
        self._scope_manager = ScopeManager(global_scope=Scope.new_global_from_module(self._module_tree.modules[0]))
        try:
            self._ast.pre_process(None, progress_bars[2], self._module_tree)
            self._ast.generate_top_level_scopes(self._scope_manager, progress_bars[3], self._module_tree)
            self._ast.generate_top_level_aliases(self._scope_manager, progress_bars[4])
            self._ast.load_super_scopes(self._scope_manager, progress_bars[5])
            self._ast.analyse_semantics(self._scope_manager, progress_bars[6])

        except SemanticError as error:
            errored_module = self._module_tree.modules.find(lambda m: self._ast.current() is m.module_ast)
            error.throw(errored_module.error_formatter)

        finally:

            # Make an output directory for the ASTs.
            if not os.path.exists("out"):
                os.makedirs("out")

            # Save the file hashes to the output file (don't need to recompile if nothing has changed).
            # Will need run steps from load_super_scopes and onwards again though.
            with open("out/file_hashes.json", "w") as file:
                file.write(json.dumps({
                    module.path: hashlib.md5(module.code.encode()).hexdigest()
                    for module in self._module_tree.modules}, indent=4))

            # Save the AST to the output file (if in debug mode).
            if self._mode == Compiler.Mode.Dev:
                for module in self._module_tree:
                    ast = module.module_ast
                    out_ast_path = module.path.replace("src", "out/ast", 1).replace(".spp", ".ast")
                    if not os.path.exists(os.path.dirname(out_ast_path)):
                        os.makedirs(os.path.dirname(out_ast_path))
                    with open(out_ast_path, "w") as file:
                        file.write(ast.print(AstPrinter()))

                out_scope_manager_path = self._src_path.replace("src", "out/smg", 1)
                if not os.path.exists(out_scope_manager_path):
                    os.makedirs(out_scope_manager_path)
                with open(out_scope_manager_path + "/scope_manager.json", "w") as file:
                    file.write(json.dumps(self._scope_manager.global_scope, indent=4))
