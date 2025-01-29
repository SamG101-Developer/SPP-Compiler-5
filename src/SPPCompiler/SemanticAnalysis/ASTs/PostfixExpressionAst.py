from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionAst(Ast, TypeInferrable, CompilerStages):
    lhs: Asts.ExpressionAst = field(default=None)
    op: Asts.PostfixExpressionOperatorAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.lhs
        assert self.op

    @std.override_method
    def __eq__(self, other: PostfixExpressionAst) -> bool:
        return isinstance(other, PostfixExpressionAst) and self.lhs == other.lhs and self.op == other.op

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer),
            self.op.print(printer)]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the postfix operation being applied to the "lhs".
        return self.op.infer_type(scope_manager, lhs=self.lhs, **kwargs)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst cannot be used as an expression for the lhs.
        if isinstance(self.lhs, Asts.TokenAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.lhs)

        # Analyse the "lhs" and "op".
        self.lhs.analyse_semantics(scope_manager, **kwargs)
        self.op.analyse_semantics(scope_manager, lhs=self.lhs, **kwargs)


__all__ = ["PostfixExpressionAst"]
