from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class LoopConditionBooleanAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    condition: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.condition is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.condition.print(printer)

    @property
    def pos_end(self) -> int:
        return self.condition.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Boolean conditions are inferred as "bool".
        return CommonTypes.Bool(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the condition.
        if isinstance(self.condition, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.condition).scopes(sm.current_scope)

        # Analyse the condition expression.
        self.condition.analyse_semantics(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(self.condition, self.condition, sm, update_memory_info=False)

        # Check the loop condition is boolean.
        return_type = self.condition.infer_type(sm)
        target_type = CommonTypes.Bool(self.pos)
        if not target_type.symbolic_eq(return_type, sm.current_scope):
            raise SemanticErrors.ExpressionNotBooleanError().add(
                self.condition, return_type, "loop").scopes(sm.current_scope)


__all__ = [
    "LoopConditionBooleanAst"]
