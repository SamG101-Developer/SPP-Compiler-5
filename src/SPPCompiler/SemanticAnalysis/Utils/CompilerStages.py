from __future__ import annotations

from typing import Any, Union

from llvmlite import ir as llvm

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

type PreProcessingContext = Union[
    Asts.ClassPrototypeAst,
    Asts.ClassAttributeAst,
    Asts.FunctionPrototypeAst,
    Asts.GlobalConstantAst,
    Asts.ModulePrototypeAst,
    Asts.SupPrototypeFunctionsAst,
    Asts.SupPrototypeExtensionAst,
    Asts.UseStatementAst,
    None]


class CompilerStages:
    def pre_process(self, ctx: PreProcessingContext) -> None:
        """!
        The preprocessor stage performs mutations on ASTs, introduces new ASTs, and removes some ASTs. This allows for
        single-method processing of multiple ASTs, such as functions vs types with function classes superimposed over
        them. This stage directly affects what symbols are generated.
        @param context The pre-processing context that owns the AST being pre-processed.
        """

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        """!
        The generate top-level scopes stage generates all module and superimposition level scopes and symbols. This
        includes classes, attributes, functions, sup-methods, aliases and global constants. No generation is done for
        symbols inside functions. The symbols are generated here so that they can be used in any module, allowing for
        circular imports.
        @param sm The scope manager
        """

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        """!
        The generate top-level aliases stage generates all aliases at the module/sup level. This must come after the
        symbol generation stage, as it requires symbol knowledge to attach the correct "old types". It must also come
        before the load sup scopes stage, because superimposing over aliases requires the alias to exist beforehand, in
        any order of compilation.
        @param sm The scope manager
        @param kwargs Additional keyword arguments.
        """

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        """!
        The load super scopes stage links all super scopes to classes. This allows a type to know what attributes and
        methods are on its superclasses, and is requires for symbol resolution.
        @param sm The scope manager
        @param kwargs Additional keyword arguments.
        """

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """!
        The semantic analysis stage is the most complex, and final analysis, stage of the semantic pipeline. This stage
        performs all the semantic checks, type inference, and type checking. This stage requires all symbols to be
        generated, and all types to be aliased, loaded, and post-processed. All functions scopes are inspected.
        @param sm The scope manager
        @param kwargs Additional keyword arguments.
        """

    def generate_llvm_declarations(self, sm: ScopeManager, llvm_module: llvm.Module, **kwargs) -> Any:
        """!
        The LLVM declaration generation stage is the penultimate stage of the compiler. This stage generates the LLVM IR
        declarations for the module, with no implementations. This is to load all the symbols into the LLVM context.
        @todo This stage is not yet implemented.
        """

    def generate_llvm_definitions(
            self, sm: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None,
            block: llvm.Block = None, **kwargs) -> Any:
        """!
        The LLVM definition generation stage is the final stage of the compiler. This stage generates the LLVM IR
        definitions for the module, with implementations. This is to generate the actual code for the module. All the
        definitions will have associated declarations from the previous stage.
        @todo This stage is not yet implemented.
        """


__all__ = [
    "CompilerStages",
    "PreProcessingContext"]
