from __future__ import annotations
from fastenum import Enum
from typing import TYPE_CHECKING
import json, os

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree
    from SPPCompiler.SemanticAnalysis.Analyser import Analyser
    from SPPCompiler.SemanticAnalysis.ASTs.ProgramAst import ProgramAst


class Compiler:
    class Mode(Enum):
        Debug = "d"
        Release = "r"

    _src_path: str
    _module_tree: ModuleTree
    _mode: Mode
    _ast: ProgramAst
    _analyser: Analyser

    def __init__(self, src_path: str, mode: Mode) -> None:
        from SPPCompiler.Compiler.ModuleTree import ModuleTree
        from SPPCompiler.SemanticAnalysis.ASTs.ProgramAst import ProgramAst

        # Register the parameters against the instance.
        self._src_path = src_path
        self._module_tree = ModuleTree(src_path)
        self._mode = mode
        self._ast = ProgramAst(0, Seq())

        # Compile the modules.
        self.compile()

    def compile(self) -> None:
        from SPPCompiler.LexicalAnalysis.Lexer import Lexer
        from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter
        from SPPCompiler.SemanticAnalysis.Analyser import Analyser
        from SPPCompiler.SyntacticAnalysis.Parser import Parser
        from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter

        # Lexing stage.
        for module in self._module_tree.modules:
            module.code = open(module.path).read()
            module.token_stream = Lexer(module.code).lex()
            module.error_formatter = ErrorFormatter(module.token_stream, module.path)

        # Parsing stage.
        for module in self._module_tree.modules:
            module.module_ast = Parser(module.token_stream, module.path, module.error_formatter).parse()

        # Save the modules into the ProgramAst
        self._ast.modules = Seq([module.module_ast for module in self._module_tree.modules])
        self._analyser = Analyser(self._ast)
        self._analyser.analyse(self._module_tree)

        # Save the AST to the output file (if in debug mode).
        if self._mode == Compiler.Mode.Debug:
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

    def output_process(self) -> None:
        ...
