from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class CaseExpressionBranchAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """!
    The
    """

    op: Optional[Asts.TokenAst] = field(default=None)
    patterns: Seq[Asts.PatternVariantAst] = field(default_factory=Seq)
    guard: Optional[Asts.PatternGuardAst] = field(default=None)
    body: Asts.InnerScopeAst = field(default_factory=lambda: Asts.InnerScopeAst())

    def __post_init__(self) -> None:
        self.body = self.body or Asts.InnerScopeAst(pos=self.pos)

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
            self.op.print(printer) if self.op else "",
            self.patterns.print(printer, ", "),
            self.guard.print(printer) if self.guard else "",
            self.body.print(printer) if self.body else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """!
        The type of a case's branch is the type of the inner scope, which in turn is the type of the final expression.
        @param sm The scope manager.
        @param kwargs Additional keyword arguments.
        """

        # Infer the type of the body.
        return self.body.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        """!
        Analysing a branch requires analysing each part in order: the patterns, body and guard. There are no extra
        checks unique to the branch itself.
        @param sm The scope manager.
        @param condition The condition of the case expression.
        @param kwargs Additional keyword arguments.
        """

        # Create a new scope for the pattern block.
        sm.create_and_move_into_new_scope(f"<pattern:{self.pos}>")

        # Analyse the patterns, guard and body.
        for p in self.patterns:
            p.analyse_semantics(sm, cond, **kwargs)
        if self.guard:
            self.guard.analyse_semantics(sm, **kwargs)
        self.body.analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()


__all__ = [
    "CaseExpressionBranchAst"]
