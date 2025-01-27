from __future__ import annotations
from dataclasses import dataclass, field
from llvmlite import ir as llvm
from typing import Any, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ClassAttributeAst import ClassAttributeAst
    from SPPCompiler.SemanticAnalysis.ASTs.ClassPrototypeAst import ClassPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.GlobalConstantAst import GlobalConstantAst
    from SPPCompiler.SemanticAnalysis.ASTs.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementAst import UseStatementAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

type PreProcessingContext = Union[
    ClassPrototypeAst, ClassAttributeAst, FunctionPrototypeAst, GlobalConstantAst, ModulePrototypeAst,
    SupPrototypeFunctionsAst, UseStatementAst, None]


# Todo:
#  - Rename functions:
#  1. pre_process -> pre_process
#  2. generate_symbols -> generate_exported_symbols
#  3. alias_types -> link_aliases
#  4. load_sup_scopes -> link_super_scopes
#  5. inject_sup_scopes -> postprocess_super_scopes
#  6. alias_types_regeneration -> generic_regenerate_aliases
#  7. regenerate_generic_types -> generic_regenerate_types
#  8. analyse_semantics -> analyse_semantics
#  9. generate_llvm -> generate_llvm


@dataclass
class CompilerStages:
    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)
    _scope: Optional[Scope] = field(default=None, kw_only=True, repr=False)

    def pre_process(self, context: PreProcessingContext) -> None:
        """
        The preprocessor stage performs mutations on ASTs, introduces new ASTs, and removes some ASTs. This allows for
        single-method processing of multiple ASTs, such as functions vs types with function classes superimposed over
        them. This stage directly affects what symbols are generated.
        """

        self._ctx = context

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        """
        The generate top-level scopes stage generates all module and superimposition level scopes and symbols. This
        includes classes, attributes, functions, sup-methods, aliases and global constants. No generation is done for
        symbols inside functions. The symbols are generated here so that they can be used in any module, allowing for
        circular imports.
        """
        self._scope = scope_manager.current_scope

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        """
        The generate top-level aliases stage generates all aliases at the module/sup level. This must come after the
        symbol generation stage, as it requires symbol knowledge to attach the correct "old types". It must also come
        before the load sup scopes stage, because superimposing over aliases requires the alias to exist beforehand, in
        any order of compilation.
        """

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        """
        The load super scopes stage links all super scopes to classes. This allows a type to know what attributes and
        methods are on its superclasses, and is requires for symbol resolution.
        """

    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        """
        The postprocess super scopes stage performs checks that must happen after the super scopes have been injected,
        but that are separate from the next stage (type-regeneration). This includes things that require knowledge of
        all the super scopes.
        """

    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        """
        The regenerate generic aliases stage is the generic type regeneration stage exclusive to type-aliases. This is
        to ensure the aliases' old type has been generically substituted correctly, and is required before the rest of
        the regular type's generic substitution is regenerated. This is because regular type regeneration may rely on
        aliased types.
        """

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        """
        The regenerate generic types stage takes all the pruned generic types, and regenerated them with full knowledge
        of substitutions and inference. This is required as the generic types were placeholders earlier in the
        compilation stages.
        """

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        """
        The semantic analysis stage is the most complex, and final analysis, stage of the semantic pipeline. This stage
        performs all the semantic checks, type inference, and type checking. This stage requires all symbols to be
        generated, and all types to be aliased, loaded, and post-processed. All functions scopes are inspected.
        """

    def generate_llvm_declarations(self, scope_handler: ScopeManager, llvm_module: llvm.Module, **kwargs) -> Any:
        """
        The LLVM declaration generation stage is the penultimate stage of the compiler. This stage generates the LLVM IR
        declarations for the module, with no implementations. This is to load all the symbols into the LLVM context.
        """

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        """
        The LLVM definition generation stage is the final stage of the compiler. This stage generates the LLVM IR
        definitions for the module, with implementations. This is to generate the actual code for the module. All the
        definitions will have associated declarations from the previous stage.
        """
