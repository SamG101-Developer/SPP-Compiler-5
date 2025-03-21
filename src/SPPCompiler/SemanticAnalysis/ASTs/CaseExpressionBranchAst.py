from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class CaseExpressionBranchAst(Ast, TypeInferrable):
    comp_operator: Optional[Asts.TokenAst] = field(default=None)
    patterns: Seq[Asts.PatternVariantAst] = field(default_factory=Seq)
    guard: Optional[Asts.PatternGuardAst] = field(default=None)
    body: Asts.InnerScopeAst = field(default_factory=lambda: Asts.InnerScopeAst())

    @staticmethod
    def from_else_to_else_case(pos: int, else_case: Asts.PatternVariantElseCaseAst) -> CaseExpressionBranchAst:
        else_pattern = Asts.PatternVariantElseAst(pos=pos, tok_else=else_case.tok_else)
        case_branch = CaseExpressionBranchAst(
            pos=pos, patterns=Seq([else_pattern]), body=Asts.InnerScopeAst(members=Seq([else_case.case_expression])))
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

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type of the body.
        return self.body.infer_type(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, condition: Asts.ExpressionAst = None, **kwargs) -> None:
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
