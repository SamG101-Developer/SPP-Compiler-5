from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.LoopConditionAst import LoopConditionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LoopElseStatementAst import LoopElseStatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst


@dataclass
class LoopExpressionAst(Ast, TypeInferrable, CompilerStages):
    tok_loop: TokenAst
    condition: LoopConditionAst
    body: InnerScopeAst[StatementAst]
    else_block: Optional[LoopElseStatementAst]

    _loop_type_info: dict = field(default_factory=dict, init=False, repr=False)
    _loop_type_index: int = field(default=0, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_loop.print(printer) + " ",
            self.condition.print(printer) + " ",
            self.body.print(printer) + "\n",
            self.else_block.print(printer) if self.else_block else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Get the loop type set by exit expressions inside the loop.
        loop_type = self._loop_type_info.get(self._loop_type_index, (None, None))[1]
        if not loop_type:
            void_type = CommonTypes.Void(self.pos)
            loop_type = InferredType.from_type(void_type)
        return loop_type

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Create a new scope for the loop body.
        scope_manager.create_and_move_into_new_scope(f"<loop:{self.pos}>")
        self.condition.analyse_semantics(scope_manager, **kwargs)

        # Analyse twice (for memory checks).
        for i in range(("loop_count" not in kwargs) + 1):
            kwargs["loop_count"] = kwargs.get("loop_count", 0) + 1
            kwargs["loop_types"] = kwargs.get("loop_types", {})
            kwargs["loop_ast"] = self
            self._loop_type_info = kwargs["loop_types"]
            self._loop_type_index = kwargs["loop_count"]
            self.body.analyse_semantics(scope_manager, **kwargs)
            kwargs["loop_count"] -= 1

        # Move out of the loop scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["LoopExpressionAst"]
