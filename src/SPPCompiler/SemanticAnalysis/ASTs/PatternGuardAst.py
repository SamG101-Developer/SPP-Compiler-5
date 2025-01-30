from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternGuardAst(Ast):
    guard_token: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwAnd))
    expression: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.expression

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.guard_token.print(printer),
            self.expression.print(printer)]
        return "".join(string)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expression, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.expression)

        # Analyse the expression.
        self.expression.analyse_semantics(scope_manager, **kwargs)

        # Check the guard's type is boolean.
        target_type = CommonTypes.Bool(self.pos)
        return_type = self.expression.infer_type(scope_manager).type
        if not target_type.symbolic_eq(return_type, scope_manager.current_scope):
            raise SemanticErrors.ExpressionNotBooleanError().add(self.expression, return_type, "pattern guard")


__all__ = ["PatternGuardAst"]
