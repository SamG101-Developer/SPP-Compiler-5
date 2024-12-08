from __future__ import annotations
from dataclasses import dataclass, field
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
    SupPrototypeFunctionsAst, UseStatementAst]


@dataclass
class CompilerStages:
    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)
    _scope: Optional[Scope] = field(default=None, kw_only=True, repr=False)

    def pre_process(self, context: PreProcessingContext) -> None:
        # Preprocess the AST by reconfiguring it before any scoping or symbol generation is performed.
        self._ctx = context

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Generate scopes for all prototypes, (not inside function scopes: see analyse_semantics).
        self._scope = scope_manager.current_scope

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Perform any type-aliasing operations.
        pass

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes for all prototypes.
        pass

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Load stage 2 of the super scopes for all prototypes. todo: looking to remove
        pass

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        # Regenerate aliases' generics.
        pass

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Regenerate all other generics.
        pass

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the semantics of the AST.
        pass

    def generate_llvm(self, scope_handler: ScopeManager, **kwargs) -> Any:
        # Generate the LLVM IR for the AST.
        pass
