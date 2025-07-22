from __future__ import annotations

import operator
from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class IterExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The IterExpressionAst represents is used to unpack a yielded value from a generator, allowing the inspection of: a
    value, no-value, error, or exhausted state.
    """

    kw_iter: Asts.TokenAst = field(default=None)
    """The ``case`` keyword representing the case expression."""

    cond: Asts.ExpressionAst = field(default=None)
    """The condition of the case expression."""

    kw_of: Asts.TokenAst = field(default=None)
    """The optional ``of`` keyword indicating a subsequent list of patterns."""

    branches: list[Asts.IterExpressionBranchAst] = field(default_factory=list)
    """The branches that the condition can be matched against."""

    def __post_init__(self) -> None:
        self.kw_case = self.kw_iter or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwIter)
        self.kw_of = self.kw_of or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwOf)

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = [
            self.kw_iter.print(printer),
            self.cond.print(printer),
            self.kw_of.print(printer),
            *[branch.print(printer) for branch in self.branches]]
        return " ".join(string)

    def __str__(self) -> str:
        return f"{self.kw_iter}{self.cond} {self.kw_of} {" ".join([str(branch) for branch in self.branches])}"

    @property
    def pos_end(self) -> int:
        return self.kw_of.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # The checks here only apply when assigning from this expression.
        branch_inferred_types = [b.infer_type(sm, **kwargs) for b in self.branches]

        # All branches must return the same type.
        zeroth_branch_type = branch_inferred_types[0]
        if mismatch := [x for x in branch_inferred_types[1:] if not AstTypeUtils.symbolic_eq(x, zeroth_branch_type, sm.current_scope, sm.current_scope)]:
            raise SemanticErrors.CaseBranchesConflictingTypesError().add(
                zeroth_branch_type, mismatch[0]).scopes(sm.current_scope)

        # Ensure there is a full set of branches for different generator types.
        cond_type = self.cond.infer_type(sm, **kwargs)
        pattern_types = {type(b.pattern) for b in self.branches}

        # For a GenOpt, ensure there is a "value", "no-value" and "exhausted" branch.
        ignore_else = kwargs.pop("ignore_else", False)
        if AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATED_OPT, cond_type.without_generics, sm.current_scope, sm.current_scope) and not ignore_else:
            if missing := {Asts.IterPatternVariableAst, Asts.IterPatternNoValueAst, Asts.IterPatternExhaustedAst} - pattern_types:
                raise SemanticErrors.IterExpressionBranchMissingError().add(
                    self.cond, cond_type, self, list(missing)[0]).scopes(sm.current_scope)

        # For a GenRes, ensure there is a "value", "exception" and "exhausted" branch.
        elif AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATED_RES, cond_type.without_generics, sm.current_scope, sm.current_scope) and not ignore_else:
            if missing := {Asts.IterPatternVariableAst, Asts.IterPatternExceptionAst, Asts.IterPatternExhaustedAst} - pattern_types:
                raise SemanticErrors.IterExpressionBranchMissingError().add(
                    self.cond, cond_type, self, list(missing)[0]).scopes(sm.current_scope)

        # For a Gen, ensure there is a "value" and "exhausted" branch.
        elif AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATED, cond_type.without_generics, sm.current_scope, sm.current_scope) and not ignore_else:
            if missing := {Asts.IterPatternVariableAst, Asts.IterPatternExhaustedAst} - pattern_types:
                raise SemanticErrors.IterExpressionBranchMissingError().add(
                    self.cond, cond_type, self, list(missing)[0]).scopes(sm.current_scope)

        # Return the branches' return type (there is always 1+ branch).
        return branch_inferred_types[0]

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the condition.
        if isinstance(self.cond, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.cond).scopes(sm.current_scope)

        # Analyse the condition (outside the new scope).
        self.cond.analyse_semantics(sm, **kwargs)

        # Create the scope for the case expression.
        sm.create_and_move_into_new_scope(f"<iter-expr#{self.pos}>")

        # Check each type of branch is unique.
        pattern_types = []
        for branch in self.branches:
            if type(branch.pattern) in map(operator.itemgetter(1), pattern_types):
                raise SemanticErrors.IterExpressionBranchTypeDuplicateError().add(
                    [p for p, _ in pattern_types if type(p) is type(branch.pattern)][0], branch).scopes(sm.current_scope)
            pattern_types.append((branch.pattern, type(branch.pattern)))

        # Check branch compatibility with the condition (value and exhaustion match all generator types).
        cond_type = self.cond.infer_type(sm, **kwargs)

        # IterPatternNoValue -> must be a GenOpt condition.
        if Asts.IterPatternNoValueAst in map(operator.itemgetter(1), pattern_types) and not AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATED_OPT, cond_type.without_generics, sm.current_scope, sm.current_scope):
            pattern = [b for b, t in pattern_types if t is Asts.IterPatternNoValueAst][0]
            raise SemanticErrors.IterExpressionBranchIncompatibleError().add(
                self.cond, cond_type, pattern, CommonTypesPrecompiled.EMPTY_GEN_OPT).scopes(sm.current_scope)

        # IterPatternException -> must be a GenRes condition.
        if Asts.IterPatternExceptionAst in map(operator.itemgetter(1), pattern_types) and not AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATED_RES, cond_type.without_generics, sm.current_scope, sm.current_scope):
            pattern = [b for b, t in pattern_types if t is Asts.IterPatternExceptionAst][0]
            raise SemanticErrors.IterExpressionBranchIncompatibleError().add(
                self.cond, cond_type, pattern, CommonTypesPrecompiled.EMPTY_GEN_RES).scopes(sm.current_scope)

        # Analyse each branch of the case expression.
        for branch in self.branches:
            branch.analyse_semantics(sm, cond=self.cond, **kwargs)

        # Move out of the case expression scope.
        sm.move_out_of_current_scope()

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Ew
        Asts.CaseExpressionAst.check_memory(self, sm, **kwargs)


__all__ = ["IterExpressionAst"]
