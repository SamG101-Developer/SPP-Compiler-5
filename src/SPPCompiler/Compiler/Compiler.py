from __future__ import annotations

import hashlib
import json
import os
import time
from pprint import pprint
from typing import TYPE_CHECKING

from fastenum import Enum

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree
    from SPPCompiler.SemanticAnalysis.Analyser import Analyser
    from SPPCompiler.Compiler.Program import Program


class Compiler:
    class Mode(Enum):
        Dev = "d"
        Rel = "r"

    _src_path: str
    _module_tree: ModuleTree
    _mode: Mode
    _ast: Program
    _analyser: Analyser

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
        from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter
        from SPPCompiler.SemanticAnalysis.Analyser import Analyser
        from SPPCompiler.SyntacticAnalysis.ErrorFormatter import ErrorFormatter
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser
        from SPPCompiler.Utils.ProgressBar import ProgressBar
        time_start = time.time()

        progress_bars = [
            ProgressBar("Lexing.........................", self._module_tree.modules.length),
            ProgressBar("Parsing........................", self._module_tree.modules.length)]

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
            module_namespace = module_namespace[module_namespace.index("src") + 1 : -1]
            if module.path.startswith(os.path.sep + "vcs") and not module_namespace:
                self._module_tree.modules.remove(module)

        # Save the modules into the ProgramAst
        self._ast.modules = Seq([module.module_ast for module in self._module_tree.modules])
        self._analyser = Analyser(self._ast)
        self._analyser.analyse(self._module_tree)

        # Print compile time.
        time_end = time.time()
        # print(f"Compile time: {time_end - time_start:.2}s")

        # Make an output directory for the ASTs.
        if not os.path.exists("out"):
            os.makedirs("out")

        # Save the file hashes to the output file (don't need to recompile if nothing has changed).
        with open("out/file_hashes.json", "w") as file:
            file.write(json.dumps({module.path: hashlib.md5(module.code.encode()).hexdigest() for module in self._module_tree.modules}, indent=4))

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
                file.write(json.dumps(self._analyser._scope_manager.global_scope, indent=4))
