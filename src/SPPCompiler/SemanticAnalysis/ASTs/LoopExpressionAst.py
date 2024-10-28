from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.LoopConditionAst import LoopConditionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LoopElseStatementAst import LoopElseStatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst


@dataclass
class LoopExpressionAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
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
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        scope_manager.create_and_move_into_new_scope(f"<loop:{self.pos}>")
        self.body.analyse_semantics(scope_manager, **kwargs)
        scope_manager.move_out_of_current_scope()


__all__ = ["LoopExpressionAst"]
