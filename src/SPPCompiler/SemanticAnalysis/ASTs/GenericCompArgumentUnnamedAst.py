from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericCompArgumentUnnamedAst(Ast, Ordered):
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.value
        self._variant = "Unnamed"

    @std.override_method
    def __eq__(self, other: GenericCompArgumentUnnamedAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return isinstance(other, GenericCompArgumentUnnamedAst) and self.value == other.value

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value)

        # Analyse the value of the unnamed argument.
        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericCompArgumentUnnamedAst"]
