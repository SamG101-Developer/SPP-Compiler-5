from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UnaryExpressionAst(Ast, TypeInferrable):
    op: Asts.UnaryExpressionOperatorAst = field(default=None)
    rhs: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.op
        assert self.rhs

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.op.print(printer),
            self.rhs.print(printer)]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the unary operation being applied to the "rhs".
        return self.op.infer_type(scope_manager, rhs=self.rhs, **kwargs)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the rhs.
        if isinstance(self.rhs, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.rhs)

        # Analyse the "op" and the "rhs".
        self.op.analyse_semantics(scope_manager, rhs=self.rhs, **kwargs)
        self.rhs.analyse_semantics(scope_manager, **kwargs)


__all__ = ["UnaryExpressionAst"]
