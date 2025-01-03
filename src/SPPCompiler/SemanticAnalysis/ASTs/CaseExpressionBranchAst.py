from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantElseCaseAst import PatternVariantElseCaseAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternGuardAst import PatternGuardAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantAst import PatternVariantAst
    from SPPCompiler.SemanticAnalysis.ASTs.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst


@dataclass
class CaseExpressionBranchAst(Ast, TypeInferrable, CompilerStages):
    comp_operator: Optional[TokenAst]
    patterns: Seq[PatternVariantAst]
    guard: Optional[PatternGuardAst]
    body: Optional[InnerScopeAst[StatementAst]]

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import InnerScopeAst

        # Convert the patterns into a sequence.
        self.patterns = Seq(self.patterns)
        self.body = self.body or InnerScopeAst.default()

    @staticmethod
    def from_else_to_else_case(pos: int, else_case: PatternVariantElseCaseAst) -> CaseExpressionBranchAst:
        from SPPCompiler.SemanticAnalysis import InnerScopeAst, PatternVariantElseAst
        else_pattern = PatternVariantElseAst(pos, else_case.tok_else)
        case_branch  = CaseExpressionBranchAst(pos, None, Seq([else_pattern]), None, InnerScopeAst.default(Seq([else_case.case_expression])))
        return case_branch

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.comp_operator.print(printer) if self.comp_operator else "",
            self.patterns.print(printer, ", "),
            self.guard.print(printer) if self.guard else "",
            self.body.print(printer) if self.body else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the body.
        return self.body.infer_type(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, condition: ExpressionAst = None, **kwargs) -> None:
        # Create a new scope for the pattern block.
        scope_manager.create_and_move_into_new_scope(f"<pattern:{self.pos}>")

        # Analyse the patterns, guard and body.
        for p in self.patterns:
            p.analyse_semantics(scope_manager, condition, **kwargs)
        self.body.analyse_semantics(scope_manager, **kwargs)
        if self.guard:
            self.guard.analyse_semantics(scope_manager, **kwargs)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["CaseExpressionBranchAst"]
