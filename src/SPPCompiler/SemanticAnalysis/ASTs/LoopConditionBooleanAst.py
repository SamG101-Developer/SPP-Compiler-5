from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LoopConditionBooleanAst(Ast, TypeInferrable, CompilerStages):
    condition: ExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.condition.print(printer)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Boolean conditions are inferred as "bool".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        bool_type = CommonTypes.Bool(self.pos)
        return InferredType.from_type(bool_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the condition.
        if isinstance(self.condition, (TokenAst, TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.condition)

        # Analyse the condition expression.
        self.condition.analyse_semantics(scope_manager, **kwargs)
        AstMemoryHandler.enforce_memory_integrity(self.condition, self.condition, scope_manager, update_memory_info=False)

        # Check the loop condition is boolean.
        target_type = CommonTypes.Bool(self.pos)
        return_type = self.condition.infer_type(scope_manager).type
        if not target_type.symbolic_eq(return_type, scope_manager.current_scope):
            raise SemanticErrors.ExpressionNotBooleanError().add(self.condition, return_type, "loop")


__all__ = ["LoopConditionBooleanAst"]
