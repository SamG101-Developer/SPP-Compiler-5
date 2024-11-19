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
        self._ctx = context

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        self._scope = scope_manager.current_scope

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        pass

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        pass

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        pass

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        pass

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        pass

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        pass

    def generate_llvm(self, scope_handler: ScopeManager, **kwargs) -> Any:
        pass
