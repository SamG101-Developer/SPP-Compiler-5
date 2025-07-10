from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True)
class CaseExpressionBranchAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    A CaseExpressionBranchAst represents a branch of a case expression. It contains an optional operator (the "else"
    branch won't have an operator), patterns to match the CaseExpressionAst's condition against, an optional guard and
    the body.

    Each branch's patterns will be applied against the case expressions condition. Normal "if" expressions are
    re-modelled into pattern-matching structures, so a consistent analysis can be performed against all types of
    conditional branching.

    Example:

    .. code-block:: S++

        case my_value of
            is Point(0, y, z) { std::console::print("yz-axis") }
            is Point(x, 0, z) { std::console::print("xz-axis") }
            is Point(x, y, 0) { std::console::print("xy-axis") }
    """

    op: Optional[Asts.TokenAst] = field(default=None)
    """
    The optional operator for pattern comparison. This operator will be one of the 6 standard binary comparison
    operators: ``==``, ``!=``, ``<=``, ``<``, ``>=``, ``>``, or the ``is`` keyword if a destructure is taking place.
    The only reason that an operator is omitted, is if an ``else`` pattern is being used. Standard "if" expressions such
    as ``case condition { ... }`` are re-modelled as ``case condition of == true { ... }``, providing the operator.
    """

    patterns: list[Asts.PatternVariantAst] = field(default_factory=list)
    """
    The list of patterns to apply against the case expression. For normal comparisons, there can be any number of
    patterns, but for destructuring, only 1 pattern can be applied (otherwise different symbols could get introduced
    depending on the attributes provided).
    """

    guard: Optional[Asts.PatternGuardAst] = field(default=None)
    """
    An optional pattern guard to refine destructure comparisons. This allows for a destructure to be accepted with
    conditions, which also fills in the gap of multiple patterns for a destructure: ``... is Point(x, y) and x > 0``
    allows all points with a positive ``x`` value to be accepted, whilst the ``x`` symbol is still available for use.
    """

    body: Asts.InnerScopeAst = field(default=None)
    """
    The body of the branch. This contains all the statements that will be executed if this branch is chosen when the
    code is executing. It will have its own scope, nested inside the scope created for this pattern (to save destructure
    symbols).
    """

    def __post_init__(self) -> None:
        self.body = self.body or Asts.InnerScopeAst(pos=self.pos)

    @staticmethod
    def from_else_to_else_case(pos: int, else_case: Asts.PatternVariantElseCaseAst) -> CaseExpressionBranchAst:
        """
        This conversion method is a utility to remodel ``else case ...`` into ``else { case { ... } }``, maintaining
        uniform analysis over all patterns.

        This doesn't require an entire ``case`` expression remodel, only an individual branch, which is why this
        conversion method is part of this class and not the ``Asts.CaseExpressionAst`` class.

        :param pos: The position of the AST.
        :param else_case: The branch to remodel.
        :return: The remodelled branch.
        """

        else_pattern = Asts.PatternVariantElseAst(pos=pos, kw_else=else_case.kw_else)
        case_branch = CaseExpressionBranchAst(
            pos=pos, patterns=[else_pattern], body=Asts.InnerScopeAst(members=[else_case.case_expression]))
        return case_branch

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.op.print(printer) if self.op else "",
            SequenceUtils.print(printer, self.patterns, sep=", "),
            self.guard.print(printer) if self.guard else "",
            self.body.print(printer) if self.body else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return (self.guard or self.patterns[-1]).pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        The type of a case's branch is the type of the inner scope, which in turn is the type of the final expression.
        If the inner scope is empty, it will return the ``std::void::Void`` type.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The inferred type.
        """

        # Infer the type of the body.
        return self.body.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        """
        The branch analysis requires introducing a new scope (not for the body, but for the pattern destructure
        symbols). The pattern and guard are then analysed inside this scope, and then the body is analysed, creating
        another nested scope (the body scope).

        The pattern scope is required, because the guard might need to use symbols from the destructure, before the body
        scope has been created (which is why pattern symbols can't be injected directly into the body scope).

        :param sm: The scope manager.
        :param cond: The condition (from the ``Asts.CaseExpressionAst`` ast).
        :param kwargs: Additional keyword arguments.
        """

        # Create a new scope for the pattern block.
        sm.create_and_move_into_new_scope(f"<pattern#{self.pos}>")

        # Analyse the patterns, guard and body.
        for p in self.patterns:
            p.analyse_semantics(sm, cond, **kwargs)
        if self.guard:
            self.guard.analyse_semantics(sm, **kwargs)
        self.body.analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()

    def check_memory(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        """
        Do all memory checks of the attributes of this AST.

        :param sm: The scope manager.
        :param cond: The condition (from the ``Asts.CaseExpressionAst`` ast).
        :param kwargs: Additional keyword arguments.
        """

        # Move into the branch's scope.
        sm.move_to_next_scope()

        # Check the patterns, guard and body.
        for p in self.patterns:
            p.check_memory(sm, **kwargs)
        if self.guard:
            self.guard.check_memory(sm, **kwargs)
        self.body.check_memory(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()


__all__ = [
    "CaseExpressionBranchAst"]
