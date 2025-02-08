from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union

import std
from llvmlite import ir as llvm

import SPPCompiler.SemanticAnalysis as Asts
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


@dataclass
class CompilerStages:
    __friends__ = {"AnnotationAst"}

    @std.virtual_method
    def pre_process(self, context: PreProcessingContext) -> None:
        """
        The preprocessor stage performs mutations on ASTs, introduces new ASTs, and removes some ASTs. This allows for
        single-method processing of multiple ASTs, such as functions vs types with function classes superimposed over
        them. This stage directly affects what symbols are generated.
        """

    @std.virtual_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        """
        The generate top-level scopes stage generates all module and superimposition level scopes and symbols. This
        includes classes, attributes, functions, sup-methods, aliases and global constants. No generation is done for
        symbols inside functions. The symbols are generated here so that they can be used in any module, allowing for
        circular imports.
        """

    @std.virtual_method
    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        """
        The generate top-level aliases stage generates all aliases at the module/sup level. This must come after the
        symbol generation stage, as it requires symbol knowledge to attach the correct "old types". It must also come
        before the load sup scopes stage, because superimposing over aliases requires the alias to exist beforehand, in
        any order of compilation.
        """

    @std.virtual_method
    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        """
        The load super scopes stage links all super scopes to classes. This allows a type to know what attributes and
        methods are on its superclasses, and is requires for symbol resolution.
        """

    @std.virtual_method
    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        """
        The regenerate generic aliases stage is the generic type regeneration stage exclusive to type-aliases. This is
        to ensure the aliases' old type has been generically substituted correctly, and is required before the rest of
        the regular type's generic substitution is regenerated. This is because regular type regeneration may rely on
        aliased types.
        """

    @std.virtual_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        """
        The regenerate generic types stage takes all the pruned generic types, and regenerated them with full knowledge
        of substitutions and inference. This is required as the generic types were placeholders earlier in the
        compilation stages.
        """

    @std.virtual_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        """
        The semantic analysis stage is the most complex, and final analysis, stage of the semantic pipeline. This stage
        performs all the semantic checks, type inference, and type checking. This stage requires all symbols to be
        generated, and all types to be aliased, loaded, and post-processed. All functions scopes are inspected.
        """

    @std.virtual_method
    def generate_llvm_declarations(self, scope_handler: ScopeManager, llvm_module: llvm.Module, **kwargs) -> Any:
        """
        The LLVM declaration generation stage is the penultimate stage of the compiler. This stage generates the LLVM IR
        declarations for the module, with no implementations. This is to load all the symbols into the LLVM context.
        """

    @std.virtual_method
    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        """
        The LLVM definition generation stage is the final stage of the compiler. This stage generates the LLVM IR
        definitions for the module, with implementations. This is to generate the actual code for the module. All the
        definitions will have associated declarations from the previous stage.
        """
