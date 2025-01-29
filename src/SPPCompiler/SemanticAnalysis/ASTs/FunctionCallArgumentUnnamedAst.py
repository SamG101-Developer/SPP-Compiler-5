from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Self

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionCallArgumentUnnamedAst(Ast, Ordered, TypeInferrable, CompilerStages):
    convention: Asts.ConventionAst = field(default_factory=Asts.ConventionMovAst)
    tok_unpack: Optional[Asts.TokenAst] = field(default=None)
    value: Asts.ExpressionAst = field(default=None)
    _type_from_self: InferredType = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        assert self.value
        self._variant = "Unnamed"

    @std.override_method
    def __eq__(self, other: FunctionCallArgumentUnnamedAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return isinstance(other, FunctionCallArgumentUnnamedAst) and self.value == other.value

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.convention.print(printer),
            self.tok_unpack.print(printer) if self.tok_unpack is not None else "",
            self.value.print(printer)]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        inferred_type = self.value.infer_type(scope_manager, **kwargs)

        # The convention is either from the convention attribute or the symbol information.
        match self.convention, inferred_type.convention:
            case Asts.ConventionMovAst(), symbol_convention:
                convention = symbol_convention
            case _:
                convention = type(self.convention)
        return InferredType(convention=convention, type=inferred_type.type)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value)

        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["FunctionCallArgumentUnnamedAst"]
