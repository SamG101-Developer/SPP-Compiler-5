from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import copy

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.CaseExpressionBranchAst import CaseExpressionBranchAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class CaseExpressionAst(Ast, TypeInferrable, CompilerStages):
    tok_case: TokenAst
    condition: ExpressionAst
    kw_of: Optional[TokenAst]
    branches: Seq[CaseExpressionBranchAst]

    def __post_init__(self) -> None:
        # Convert the branches into a sequence.
        self.branches = Seq(self.branches)

    @staticmethod
    def from_condition_and_branches(condition: ExpressionAst, branches: Seq[CaseExpressionBranchAst], *, pos: int) -> CaseExpressionAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TokenAst

        # Create the case expression.
        return CaseExpressionAst(pos, TokenAst.default(TokenType.KwCase), condition, TokenAst.default(TokenType.KwOf), branches)

    @staticmethod
    def from_simple(c1: int, p1: TokenAst, p2: ExpressionAst, p3: InnerScopeAst, p4: Seq[CaseExpressionBranchAst]) -> CaseExpressionAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import BooleanLiteralAst, TokenAst, ParenthesizedExpressionAst
        from SPPCompiler.SemanticAnalysis import CaseExpressionBranchAst, PatternVariantExpressionAst

        # Convert condition into an "== true" comparison.
        first_pattern = PatternVariantExpressionAst(c1, BooleanLiteralAst.from_python_literal(c1, True))
        first_branch = CaseExpressionBranchAst(c1, TokenAst.default(TokenType.TkEq), Seq([first_pattern]), None, p3)
        branches = Seq([first_branch]) + p4

        # Return the case expression.
        return CaseExpressionAst(c1, p1, ParenthesizedExpressionAst.from_expression(p2, pos=p2.pos), TokenAst.default(TokenType.KwOf), branches)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_case.print(printer) + " ",
            self.condition.print(printer) + " ",
            self.kw_of.print(printer) if self.kw_of else "",
            self.branches.print(printer, "\n")]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # The checks here only apply when assigning from this expression.
        from SPPCompiler.SemanticAnalysis import PatternVariantElseAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        branch_inferred_types = self.branches.map(lambda x: x.infer_type(scope_manager)).unique()

        # All branches must return the same type.
        if branch_inferred_types.length > 1:
            raise SemanticErrors.CaseBranchesConflictingTypesError().add(branch_inferred_types[0], branch_inferred_types[1])

        # Ensure there is an "else" branch if the branches are not exhaustive.
        if not isinstance(self.branches[-1].patterns[0], PatternVariantElseAst):
            raise SemanticErrors.CaseBranchesMissingElseBranchError().add(self.condition, self.branches[-1])

        # Return the branches' return type, if there are any branches.
        if self.branches.length > 0:
            return branch_inferred_types[0]

        # Otherwise, return the void type.
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import BinaryExpressionAst, PatternVariantElseAst, TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the condition.
        if isinstance(self.condition, (TokenAst, TypeAst)):
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
            if branch.comp_operator and branch.comp_operator.token.token_type == TokenType.KwIs and branch.patterns.length > 1:
                raise SemanticErrors.CaseBranchMultipleDestructurePatternsError().add(branch.patterns[0], branch.patterns[1])

            # Make a record of the symbols' memory status in the scope before the branch is analysed.
            symbols_in_scope = scope_manager.current_scope.all_symbols().filter_to_type(VariableSymbol)
            old_symbol_mem_info = {s: (s.memory_info.ast_initialization, s.memory_info.ast_moved, s.memory_info.ast_partially_moved.copy(), s.memory_info.ast_pinned.copy(), s.memory_info.initialization_counter) for s in symbols_in_scope}
            branch.analyse_semantics(scope_manager, condition=self.condition, **kwargs)
            new_symbol_mem_info = {s: (s.memory_info.ast_initialization, s.memory_info.ast_moved, s.memory_info.ast_partially_moved.copy(), s.memory_info.ast_pinned.copy(), s.memory_info.initialization_counter) for s in symbols_in_scope}

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
            if isinstance(branch.patterns[0], PatternVariantElseAst) and branch != self.branches[-1]:
                raise SemanticErrors.CaseBranchesElseBranchNotLastError().add(branch, self.branches[-1])

            # For non-destructuring branches, combine the condition and pattern to ensure functional compatibility.
            if branch.comp_operator and branch.comp_operator.token.token_type != TokenType.KwIs:
                for pattern in branch.patterns:

                    # Check the function exists.
                    binary_ast = BinaryExpressionAst(self.pos, self.condition, branch.comp_operator, pattern.expression)
                    binary_ast.analyse_semantics(scope_manager, **kwargs)

                    # Check the function's return type is boolean.
                    # Todo: is it possible it is non-boolean? comparisons are forced, and they all have Bool return.
                    target_type = CommonTypes.Bool(self.pos)
                    return_type = binary_ast.infer_type(scope_manager).type
                    if not target_type.symbolic_eq(return_type, scope_manager.current_scope):
                        raise SemanticErrors.ExpressionNotBooleanError().add(self.condition, return_type, "case")

        # Update the memory status of the symbols.
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
