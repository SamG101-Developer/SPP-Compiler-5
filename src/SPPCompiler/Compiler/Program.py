from __future__ import annotations

import os.path
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, List

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.Lexer import Lexer
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import CompilerStages, PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.ErrorFormatter import ErrorFormatter
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Progress import Progress
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.Compiler.ModuleTree import ModuleTree, Module
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass(slots=True)
class Program(CompilerStages):
    """
    The Program class holds a list of modules and performs each stage of the compiler on them. It is interacted with
    from the Compiler class, and is used to abstract boilerplate code per compiler stage.
    """

    modules: Seq[Asts.ModulePrototypeAst] = field(default_factory=Seq, init=False, repr=False)
    """The list of module prototype ASTs (from parsing)."""

    def lex(
            self, progress_bar: Optional[Progress] = None,
            module_tree: ModuleTree = None) -> None:

        """
        Lex every module into a list of tokens. Move the list of tokens into the ``Module`` instance. Create an
        ``ErrorFormatter`` for each module, which in turns contains the token list. This allows error messages use the
        correct set of tokens depending on the source of the error.

        :param progress_bar: Progress meter for the lexing stage.
        :param module_tree: List of modules included in the compilation.
        """

        # Lexing stage.
        for module in module_tree:
            with open(os.path.join(os.getcwd(), module.path.lstrip(os.path.sep))) as fo:
                module.code = fo.read()
            progress_bar.next(module.path)
            module.token_stream = Lexer(module.code).lex()
            module.error_formatter = ErrorFormatter(module.token_stream, module.path)
        progress_bar.finish()

    def parse(
            self, progress_bar: Optional[Progress] = None,
            module_tree: ModuleTree = None) -> None:

        """
        Parse every module's tokenstream into an AST. Set the AST into the ``Module`` instance. Save the resulting
        ``ModulePrototypeAst`` nodes into the ``modules`` list on the ``Program``.

        :param progress_bar: Progress meter for the parsing stage.
        :param module_tree: List of modules included in the compilation.
        :return:
        """

        # Parsing stage.
        for module in module_tree:
            progress_bar.next(module.path)
            module.module_ast = SppParser(module.token_stream, module.path, module.error_formatter).parse()
            self.modules.append(module.module_ast)
        progress_bar.finish()

    def pre_process(
            self, context: PreProcessingContext, progress_bar: Optional[Progress] = None,
            module_tree: ModuleTree = None) -> None:

        # Pre-process all the modules.
        for module in self.modules:
            module_in_tree = [m for m in module_tree.modules if m.module_ast is module][0]
            module._name = module_in_tree.path
            progress_bar.next(module.name.value)
            module.pre_process(module)
        progress_bar.finish()

    def generate_top_level_scopes(
            self, sm: ScopeManager, progress_bar: Optional[Progress] = None,
            module_tree: ModuleTree = None) -> None:

        # Generate symbols for all the modules, including namespaces in the scope manager.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            module.generate_top_level_scopes(sm)
            sm.reset()
        progress_bar.finish()

    def generate_top_level_aliases(
            self, sm: ScopeManager, progress_bar: Optional[Progress] = None,
            module_tree: ModuleTree = None) -> None:

        # Alias types for all the modules.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            module.generate_top_level_aliases(sm)
            sm.reset()
        progress_bar.finish()

    def qualify_types(
            self, sm: ScopeManager, progress_bar: Optional[Progress] = None,
            module_tree: ModuleTree = None) -> None:

        # Alias types for all the modules.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            module.qualify_types(sm)
            sm.reset()
        progress_bar.finish()

    def load_super_scopes(self, sm: ScopeManager, progress_bar: Optional[Progress] = None, module_tree: ModuleTree = None) -> None:
        # Load the super scopes for all the modules.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            module.load_super_scopes(sm)
            sm.reset()
        progress_bar.finish()
        sm.relink_generics()

    def pre_analyse_semantics(self, sm: ScopeManager, progress_bar: Optional[Progress] = None, module_tree: ModuleTree = None) -> None:
        # Pre analyse all the top level constructs.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            module.pre_analyse_semantics(sm)
            sm.reset()
        progress_bar.finish()

    def analyse_semantics(self, sm: ScopeManager, progress_bar: Optional[Progress] = None, module_tree: ModuleTree = None) -> None:
        # Analyse the semantics for all the modules.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            module.analyse_semantics(sm)
            sm.reset()
        progress_bar.finish()

        self._validate_entry_point(sm)

    def check_memory(self, sm: ScopeManager, progress_bar: Optional[Progress] = None, module_tree: ModuleTree = None) -> None:
        # Check the memory for all the modules.
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            module.check_memory(sm)
            sm.reset()
        progress_bar.finish()

    def code_gen(self, sm: ScopeManager, progress_bar: Optional[Progress] = None, module_tree: ModuleTree = None) -> List[ir.Module]:
        # Generate the LLVM IR for all the modules.
        llvm_modules = []
        for module in self.modules:
            self._move_scope_manager_to_namespace(sm, [m for m in module_tree.modules if m.module_ast is module][0])
            progress_bar.next(module.name.value)
            llvm_modules.append(module.code_gen(sm, None, **{"root_path": module_tree._root}))
            sm.reset()
        progress_bar.finish()
        return llvm_modules

    def _validate_entry_point(self, sm: ScopeManager) -> None:
        """
        Check there is a "main" function inside the "main" module, with the matching signature of a "Vec[Str]",
        returning the "Void" type.

        :param sm: The scope manager to use for the validation.
        """

        # Get the main module.
        main_module = [m for m in self.modules if m.name.value == "main.spp"][0]

        # Check the "main" function exists with the correct signature.
        dummy_main_call = "main::main(std::vector::Vec[std::string::Str]())"
        dummy_main_call = CodeInjection.inject_code(dummy_main_call, SppParser.parse_expression, pos_adjust=0)
        sm.reset(sm.global_scope)
        try:
            dummy_main_call.analyse_semantics(sm)
        except (SemanticErrors.FunctionCallNoValidSignaturesError, SemanticErrors.IdentifierUnknownError):
            raise SemanticErrors.MissingMainFunctionError().add(main_module).scopes(sm.global_scope)

    def _move_scope_manager_to_namespace(self, sm: ScopeManager, module: Module) -> None:
        """
        Given a module path, either create or move into the namespace for the module. The scope manager tries to visit
        the next part of the namespace, and if it doesn't exist, then a new scope is created.

        :param sm: The scope manager to move into or create the namespace.
        :param module: The module to move into or create the namespace for.
        """

        from SPPCompiler.SemanticAnalysis import Asts
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        # Create the module namespace as a list of strings.
        module_namespace = module.path.strip(os.path.sep).split(os.path.sep)
        if "src" in module_namespace:
            module_namespace = module_namespace[module_namespace.index("src") + 1:]
        else:
            # skip the "vcs", "<ns>", "ffi" parts of the namespace.
            module_namespace = [module_namespace[1] + ".spp"]
        module_namespace[-1] = module_namespace[-1].split(".")[0]

        # Iterate over the parts of the module namespace.
        for part in module_namespace:

            # Convert the string part into an IdentifierAst node.
            part = Asts.IdentifierAst(-1, part)

            # If the part exists in the current scope (starting at the global scope), then move into it.
            if part in [s.name for s in sm.current_scope.children]:
                scope = [s for s in sm.current_scope.children if s.name == part][0]
                sm.reset(scope)

            # Otherwise, create a new scope and move into it, re-using the module's error formatter for the scope.
            else:
                sm.current_scope.add_symbol(namespace_symbol := NamespaceSymbol(name=part))
                scope = sm.create_and_move_into_new_scope(part, error_formatter=module.error_formatter)

                # Create a namespace symbol for this module scope.
                namespace_symbol.scope = scope
                namespace_symbol.scope._type_symbol = namespace_symbol
                namespace_symbol.scope._ast = module.module_ast


__all__ = ["Program"]
