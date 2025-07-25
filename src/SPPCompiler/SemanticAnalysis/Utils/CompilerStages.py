from __future__ import annotations

from typing import Union

from llvmlite import ir

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

type PreProcessingContext = Union[
    Asts.ClassPrototypeAst,
    Asts.ClassAttributeAst,
    Asts.FunctionPrototypeAst,
    Asts.CmpStatementAst,
    Asts.ModulePrototypeAst,
    Asts.SupPrototypeFunctionsAst,
    Asts.SupPrototypeExtensionAst,
    Asts.UseStatementAst,
    Asts.TypeStatementAst,
    None]


class CompilerStages:
    def pre_process(self, ctx: PreProcessingContext) -> None:
        """
        The preprocessor stage performs mutations on ASTs, introduces new ASTs, and removes some ASTs. This allows for
        single-method processing of multiple ASTs, such as functions vs types with function classes superimposed over
        them. This stage directly affects what symbols are generated.
        :param ctx: The pre-processing context that owns the AST being pre-processed.
        """

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        """!
        The generate top-level scopes stage generates all module and superimposition level scopes and symbols. This
        includes classes, attributes, functions, sup-methods, aliases and global constants. No generation is done for
        symbols inside functions. The symbols are generated here so that they can be used in any module, allowing for
        circular imports.
        :param sm The scope manager.
        """

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        """!
        The generate top-level aliases stage generates all aliases at the module/sup level. This must come after the
        symbol generation stage, as it requires symbol knowledge to attach the correct "old types". It must also come
        before the load sup scopes stage, because superimposing over aliases requires the alias to exist beforehand, in
        any order of compilation.
        :param sm The scope manager.
        :param kwargs Additional keyword arguments.
        """

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        """
        ...
        :param sm:
        :param kwargs:
        :return:
        """

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        ...

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        ...

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        The semantic analysis stage is the most complex, and final analysis, stage of the semantic pipeline. This stage
        performs all the semantic checks, type inference, and type checking. This stage requires all symbols to be
        generated, and all types to be aliased, loaded, and post-processed. All functions scopes are inspected.
        :param sm The scope manager.
        :param kwargs Additional keyword arguments.
        """

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        The check memory stage is the final stage of the semantic pipeline. This stage performs all the memory checks,
        and has to happen after, and not during semantic analysis, because sometimes the ASTs are analysed out of order
        to allow for type-inference. This messes up the strict order of memory checks, so the additional stage enforces
        the order of memory checks.
        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        """
        The first pass of the code generation handles declarations. This includes type declarations (no memory layout
        set), and function declarations (no body set). This is because for class attributes, the types need to have
        already been created
        :param sm: The scope manager.
        :param llvm_module: The LLVM module to generate code for.
        :param kwargs: Additional keyword arguments.
        """

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        """
        The second pass of the code generation handles definitions. This includes type definitions (memory layout set),
        and function definitions (body set).
        :param sm: The scope manager.
        :param llvm_module: The LLVM module to generate code for.
        :param kwargs: Additional keyword arguments.
        """


__all__ = [
    "CompilerStages",
    "PreProcessingContext"]
