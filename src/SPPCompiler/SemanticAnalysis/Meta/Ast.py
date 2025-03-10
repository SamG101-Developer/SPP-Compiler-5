from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import *
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class Ast(CompilerStages):
    pos: int = field(default=0)

    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)
    _scope: Optional[Scope] = field(default=None, kw_only=True, repr=False)

    def __post_init__(self) -> None:
        self._ctx = None
        self._scope = None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        ...

    @property
    def pos_end(self) -> int:
        return 0

    def __eq__(self, other: Ast) -> bool:
        return isinstance(other, Ast)

    def __str__(self) -> str:
        printer = AstPrinter()
        return self.print(printer)

    def pre_process(self, context: PreProcessingContext) -> None:
        self._ctx = context

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        self._scope = scope_manager.current_scope


__all__ = ["Ast"]
