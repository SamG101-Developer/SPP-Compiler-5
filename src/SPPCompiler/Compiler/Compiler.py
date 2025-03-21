from __future__ import annotations

import hashlib
import json
import os
from typing import Optional, TYPE_CHECKING

from fastenum import Enum

from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticError
from SPPCompiler.Utils.ProgressBar import ProgressBar
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
    """!
    The Compiler class is the entry point into compiling the entire S++ project. It creates a module tree for the whole
    project, holds instances of the lexer and parser, and calls the analyser functions. This class is also responsible
    for dumping symbols and other compiler metadata to files, if built in "dev" mode.
    """

    class Mode(Enum):
        """!
        The Mode enum is used to determine the mode in which the compiler is running. This is used to determine whether
        to dump the ASTs and other metadata to files. The "dev" mode is used for development, and the "rel" mode is used
        for release.
        """

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
        """!
        The module tree has been constructed, so perform each compiler stage for every module. This is a breadth-first
        approach, where each module is lexed, then each module is parsed, and so on. The final stage is the semantic
        analysis, which is the most complex and time-consuming stage.

        This allows for modules to refer to code in each other, and for the compiler to resolve symbols and types across
        the entire project.

        The compiler stages are described in more detail in the CompilerStages class. For each stage, the associated
        progress bar is passed into the Program class, which iterates through the modules and calls the analysis method
        and shifts the progress bar.
        """

        # Initialise the progress bars for each compiler stage.
        progress_bars = [ProgressBar(name, self._module_tree.modules.length) for name in COMPILER_STAGE_NAMES]
        progress_bar = iter(progress_bars)

        # Save the modules into the ProgramAst
        self._ast.lex(next(progress_bar), self._module_tree)
        self._ast.parse(next(progress_bar), self._module_tree)
        self._ast.modules = Seq([module.module_ast for module in self._module_tree.modules])
        self._scope_manager = ScopeManager(global_scope=Scope.new_global_from_module(self._module_tree.modules[0]))
        CommonTypesPrecompiled.initialize()

        try:
            self._ast.pre_process(None, next(progress_bar), self._module_tree)
            self._ast.generate_top_level_scopes(self._scope_manager, next(progress_bar), self._module_tree)
            self._ast.generate_top_level_aliases(self._scope_manager, next(progress_bar))
            self._ast.load_super_scopes(self._scope_manager, next(progress_bar))
            self._ast.analyse_semantics(self._scope_manager, next(progress_bar))

        except SemanticError as error:
            error.throw()

        finally:
            self.try_dump()

    def try_dump(self) -> None:
        """!
        All dumped symbols reside in the "out" folder. It is created if it not present. Each module has its AST dumped
        (showing the preprocessed changes), and the global scope is dumped to a JSON file. This includes all children
        scopes. File hashes are also saved to a JSON file, so the compiler can determine if a module has changed since
        the last compilation.

        If a module has not changed, then the lexing, parsing, preprocessing, top-level scopes, and top-level aliases
        steps can all be bypassed, and before the sup-scope is loaded in, the dumped scopes can be un-pickled and loaded
        in, saving time.

        @todo Implement the pickling and un-pickling of scopes, injection of un-pickled scopes, and skipping modules
        that will be re-injected.
        """

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
