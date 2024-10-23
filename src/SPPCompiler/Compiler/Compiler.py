from __future__ import annotations
from typing import TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.Compiler.ModuleTree import ModuleTree
    from SPPCompiler.SemanticAnalysis.Analyser import Analyser
    from SPPCompiler.SemanticAnalysis.ASTs.ProgramAst import ProgramAst


class Compiler:
    _src_path: str
    _module_tree: ModuleTree
    _mode: str
    _ast: ProgramAst
    _analyser: Analyser

    def __init__(self, src_path: str, mode: str = "d") -> None:
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
        from SPPCompiler.SyntacticAnalysis.Parser import Parser
        from SPPCompiler.SemanticAnalysis.Analyser import Analyser
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

    def output_process(self) -> None:
        ...
