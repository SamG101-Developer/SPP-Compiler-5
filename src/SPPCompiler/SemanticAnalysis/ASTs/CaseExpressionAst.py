from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class CaseExpressionAst(Ast, TypeInferrable):
    tok_case: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwCase))
    condition: Asts.ExpressionAst = field(default=None)
    kw_of: Optional[Asts.TokenAst] = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwOf))
    branches: Seq[Asts.CaseExpressionBranchAst] = field(default_factory=Seq)

    def __post_init__(self) -> None:
        assert self.condition

    @staticmethod
    def from_simple(c1: int, p1: Asts.TokenAst, p2: Asts.ExpressionAst, p3: Asts.InnerScopeAst, p4: Seq[Asts.CaseExpressionBranchAst]) -> CaseExpressionAst:
        # Convert condition into an "== true" comparison.
        first_pattern = Asts.PatternVariantExpressionAst(c1, Asts.BooleanLiteralAst.from_python_literal(c1, True))
        first_branch = Asts.CaseExpressionBranchAst(c1, comp_operator=Asts.TokenAst.raw(pos=c1, token=SppTokenType.TkEq), patterns=Seq([first_pattern]), body=p3)
        branches = Seq([first_branch]) + p4

        # Return the case expression.
        return CaseExpressionAst(c1, p1, Asts.ParenthesizedExpressionAst(pos=p2.pos, expression=p2), branches=branches)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_case.print(printer) + " ",
            self.condition.print(printer) + " ",
            self.kw_of.print(printer) if self.kw_of else "",
            self.branches.print(printer, "\n")]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # The checks here only apply when assigning from this expression.
        branch_inferred_types = self.branches.map(lambda x: x.infer_type(scope_manager)).unique()

        # All branches must return the same type.
        if branch_inferred_types.length > 1:
            raise SemanticErrors.CaseBranchesConflictingTypesError().add(branch_inferred_types[0], branch_inferred_types[1])

        # Ensure there is an "else" branch if the branches are not exhaustive.
        if not isinstance(self.branches[-1].patterns[0], Asts.PatternVariantElseAst):
            raise SemanticErrors.CaseBranchesMissingElseBranchError().add(self.condition, self.branches[-1])

        # Return the branches' return type, if there are any branches, otherwise Void.
        if self.branches.length > 0:
            return branch_inferred_types[0]
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the condition.
        if isinstance(self.condition, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.condition)

        # Analyse the condition and enforce memory integrity (outside the new scope).
        self.condition.analyse_semantics(scope_manager)
        AstMemoryHandler.enforce_memory_integrity(self.condition, self.condition, scope_manager, update_memory_info=False)

        # Create the scope for the case expression.
        scope_manager.create_and_move_into_new_scope(f"<case-expr:{self.pos}>")

        # Analyse each branch of the case expression.
        symbol_mem_info = defaultdict(Seq)
        for branch in self.branches:

            # Destructures can only use 1 pattern.
            if branch.comp_operator and branch.comp_operator.token.token_type == SppTokenType.KwIs and branch.patterns.length > 1:
                raise SemanticErrors.CaseBranchMultipleDestructurePatternsError().add(branch.patterns[0], branch.patterns[1])

            # Make a record of the symbols' memory status in the scope before the branch is analysed.
            symbols_in_scope = scope_manager.current_scope.all_symbols().filter_to_type(VariableSymbol)
            old_symbol_mem_info = {
                s: (s.memory_info.ast_initialization, s.memory_info.ast_moved, s.memory_info.ast_partially_moved.copy(), s.memory_info.ast_pinned.copy(), s.memory_info.initialization_counter)
                for s in symbols_in_scope}

            branch.analyse_semantics(scope_manager, condition=self.condition, **kwargs)
            new_symbol_mem_info = {
                s: (s.memory_info.ast_initialization, s.memory_info.ast_moved, s.memory_info.ast_partially_moved.copy(), s.memory_info.ast_pinned.copy(), s.memory_info.initialization_counter)
                for s in symbols_in_scope}

            # Reset the memory status of the symbols for the next branch to be analysed in the same state.
            for symbol, old_memory_status in old_symbol_mem_info.items():
                symbol.memory_info.ast_initialization = old_memory_status[0]
                symbol.memory_info.ast_moved = old_memory_status[1]
                symbol.memory_info.ast_partially_moved = old_memory_status[2]
                symbol.memory_info.ast_pinned = old_memory_status[3]
                symbol.memory_info.initialization_counter = old_memory_status[4]

                # Insert or append the new memory status of the symbol.
                symbol_mem_info[symbol].append((branch, new_symbol_mem_info[symbol]))

            # Check the "else" branch is the final branch (also ensures there is only 1).
            if isinstance(branch.patterns[0], Asts.PatternVariantElseAst) and branch != self.branches[-1]:
                raise SemanticErrors.CaseBranchesElseBranchNotLastError().add(branch, self.branches[-1])

            # For non-destructuring branches, combine the condition and pattern to ensure functional compatibility.
            if branch.comp_operator and branch.comp_operator.token.token_type != SppTokenType.KwIs:
                for pattern in branch.patterns:

                    # Check the function exists.
                    binary_ast = Asts.BinaryExpressionAst(self.pos, self.condition, branch.comp_operator, pattern.expression)
                    binary_ast.analyse_semantics(scope_manager, **kwargs)

                    # Check the function's return type is boolean.
                    # Todo: is it possible it is non-boolean? comparisons are forced, and they all have Bool return.
                    target_type = CommonTypes.Bool(self.pos)
                    return_type = binary_ast.infer_type(scope_manager)
                    if not target_type.symbolic_eq(return_type, scope_manager.current_scope):
                        raise SemanticErrors.ExpressionNotBooleanError().add(self.condition, return_type, "case")

        # Update the memory status of the symbols.
        # Todo: tidy this up omg
        for symbol, new_memory_info_list in symbol_mem_info.items():

            # Assuming all new memory states are consistent across branches, update to the first "new" state list.
            symbol.memory_info.ast_initialization = new_memory_info_list[0][1][0]
            symbol.memory_info.ast_moved = new_memory_info_list[0][1][1]
            symbol.memory_info.ast_partially_moved = new_memory_info_list[0][1][2]
            symbol.memory_info.ast_pinned = new_memory_info_list[0][1][3]

            # Check the new memory status for each symbol is consistent across all branches.
            for branch, memory_info_list in new_memory_info_list:

                # Check for consistent initialization.
                if new_memory_info_list[0][1][0] != memory_info_list[0]:
                    symbol.memory_info.is_inconsistently_initialized = ((self.branches[0], new_memory_info_list[0][1][0]), (branch, memory_info_list[0]))

                # Check for consistent movement.
                if new_memory_info_list[0][1][1] != memory_info_list[1]:
                    symbol.memory_info.is_inconsistently_moved = ((self.branches[0], new_memory_info_list[0][1][1]), (branch, memory_info_list[1]))

                # Check for consistent partial movement.
                if new_memory_info_list[0][1][2] != memory_info_list[2]:
                    symbol.memory_info.is_inconsistently_partially_moved = ((self.branches[0], new_memory_info_list[0][1][2]), (branch, memory_info_list[2]))

                # Check for consistent pinning.
                if new_memory_info_list[0][1][3] != memory_info_list[3]:
                    symbol.memory_info.is_inconsistently_pinned = ((self.branches[0], new_memory_info_list[0][1][3]), (branch, memory_info_list[3]))

        # Move out of the case expression scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["CaseExpressionAst"]
