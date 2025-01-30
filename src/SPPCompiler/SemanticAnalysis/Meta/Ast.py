from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import std
from llvmlite import ir as llvm

from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import *
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class Ast(CompilerStages, std.TypeChecker.BaseObject):
    pos: int = field(default=-1)

    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)
    _scope: Optional[Scope] = field(default=None, kw_only=True, repr=False)

    def __post_init__(self) -> None:
        self._ctx = None
        self._scope = None

    @ast_printer_method
    @std.abstract_method
    def print(self, printer: AstPrinter) -> str:
        ...

    @std.virtual_method
    def __eq__(self, other: Ast) -> bool:
        return isinstance(other, Ast)

    def __str__(self) -> str:
        printer = AstPrinter()
        return self.print(printer)

    @std.virtual_method
    @std.override_method
    def pre_process(self, context: PreProcessingContext) -> None:
        self._ctx = context

    @std.virtual_method
    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        self._scope = scope_manager.current_scope

    @std.virtual_method
    @std.override_method
    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        ...

    @std.virtual_method
    @std.override_method
    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        ...

    @std.virtual_method
    @std.override_method
    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        ...

    @std.virtual_method
    @std.override_method
    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        ...

    @std.virtual_method
    @std.override_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        ...

    @std.virtual_method
    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        ...

    @std.virtual_method
    @std.override_method
    def generate_llvm_declarations(self, scope_handler: ScopeManager, llvm_module: llvm.Module, **kwargs) -> Any:
        ...

    @std.virtual_method
    @std.override_method
    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        ...


__all__ = ["Ast"]
