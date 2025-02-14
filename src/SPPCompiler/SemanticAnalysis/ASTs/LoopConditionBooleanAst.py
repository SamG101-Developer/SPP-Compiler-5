from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LoopConditionBooleanAst(Ast, TypeInferrable):
    condition: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.condition

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.condition.print(printer)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        # Boolean conditions are inferred as "bool".
        return InferredTypeInfo(CommonTypes.Bool(self.pos))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the condition.
        if isinstance(self.condition, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.condition)

        # Analyse the condition expression.
        self.condition.analyse_semantics(scope_manager, **kwargs)
        AstMemoryHandler.enforce_memory_integrity(
            self.condition, self.condition, scope_manager, update_memory_info=False)

        # Check the loop condition is boolean.
        return_type = self.condition.infer_type(scope_manager)
        target_type = InferredTypeInfo(CommonTypes.Bool(self.pos))
        if not target_type.symbolic_eq(return_type, scope_manager.current_scope):
            raise SemanticErrors.ExpressionNotBooleanError().add(self.condition, return_type, "loop")


__all__ = ["LoopConditionBooleanAst"]
