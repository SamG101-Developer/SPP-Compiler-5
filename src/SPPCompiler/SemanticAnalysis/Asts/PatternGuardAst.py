from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class PatternGuardAst(Asts.Ast):
    tok_guard: Asts.TokenAst = field(default=None)
    expression: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_guard = self.tok_guard or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwAnd)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_guard.print(printer),
            self.expression.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.expression.pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expression, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.expression).scopes(sm.current_scope)

        # Analyse the expression.
        self.expression.analyse_semantics(sm, **kwargs)

        # Check the guard's type is boolean.
        target_type = CommonTypes.Bool(self.pos)
        return_type = self.expression.infer_type(sm)
        if not AstTypeUtils.symbolic_eq(target_type, return_type, sm.current_scope, sm.current_scope):
            raise SemanticErrors.ExpressionNotBooleanError().add(
                self.expression, return_type, "pattern guard").scopes(sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self.expression.check_memory(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(
            self.expression, self.tok_guard, sm, check_move=True, check_partial_move=True, check_pins=True,
            check_move_from_borrowed_ctx=True, mark_moves=True)


__all__ = [
    "PatternGuardAst"]
