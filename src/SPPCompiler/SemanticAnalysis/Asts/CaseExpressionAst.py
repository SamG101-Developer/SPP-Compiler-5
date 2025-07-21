from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from llvmlite import ir
from SPPCompiler.Utils.Functools import reduce

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils, LightweightMemoryInfo
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import SequenceUtils


# Todo: re consistency, unless there is an "else" block, then even 1 branch will could create inconsistencies: add to
#  test.


@dataclass(slots=True)
class CaseExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The CaseExpressionAst represents a conditional jumping structure in S++. Case expressions are highly flexible, and
    can be used as regular if-else expressions, or pattern matching by using the "of" keyword. A list of branches is
    maintained, and the main analysis focus of the entire case expression is ensuring consistency memory status across
    these branches, ie are all symbols equally initialized at the end of the branches.

    Example (regular):

    .. code-block:: S++

        case my_value == 100 {
            ...
        }
        else case some_other_condition {
            ...
        }
        else {
            ...
        }

    Example (pattern):

    .. code-block:: S++

        case my_object of
            is MyObject(a=1, b=[0, ..], ..) { ... }
            is MyObject(a=1, b=[1, ..], ..) { ... }
            is MyObject(c=(.., 1, _, 0), ..) { ... }
        else {
            ...
        }
    """

    kw_case: Asts.TokenAst = field(default=None)
    """The ``case`` keyword representing the case expression."""

    cond: Asts.ExpressionAst = field(default=None)
    """The condition of the case expression."""

    kw_of: Optional[Asts.TokenAst] = field(default=None)
    """The optional ``of`` keyword indicating a subsequent list of patterns."""

    branches: list[Asts.CaseExpressionBranchAst] = field(default_factory=list)
    """The branches that the condition can be matched against."""

    _binary_pattern_conversions: dict[int, list] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.kw_case = self.kw_case or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwCase)
        self.kw_of = self.kw_of or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwOf)

    def __hash__(self) -> int:
        return id(self)

    @staticmethod
    def from_simple(
            p1: Asts.TokenAst, p2: Asts.ExpressionAst, p3: Asts.InnerScopeAst,
            p4: list[Asts.CaseExpressionBranchAst]) -> CaseExpressionAst:

        """
        The "from_simple" static method acts as a pseudo-constructor to create a case expression from the singular
        expression in the condition. It is converted into a partial fragment pattern match, to provide consistent
        analysis with other case patterns (pattern matching).

        The expression:

        .. code-block:: S++

            case some_condition { ... }

        Becomes:

        .. code-block:: S++

            case some_condition of
                == true { ... }

        The method works recursively with "p4", as this sequence is a list of other converted branches, called from the
        parser. This means that "branches" is effectively a list of case expressions, that will nest into "else" blocks
        after each conversion:

        The expressions:

        .. code-block:: S++

            case some_condition { ... }
            else case other_condition { ... }
            else { ... }

        Become:

        .. code-block:: S++

            case some_condition of
                == true { ... }
                else {
                    case some_other_condition of
                        == true { ... }
                        else {
                            ...
                        }

        :param p1: The "case" keyword.
        :param p2: The case expression/condition.
        :param p3: The inner scope body.
        :param p4: Subsequent branches.
        :return: The restructured case expression.
        """

        # Convert condition into an "== true" comparison.
        first_pattern = Asts.PatternVariantExpressionAst(p1.pos, expr=Asts.BooleanLiteralAst.from_python_literal(p1.pos, True))
        first_branch = Asts.CaseExpressionBranchAst(p1.pos, op=Asts.TokenAst.raw(token_type=SppTokenType.TkEq), patterns=[first_pattern], body=p3)
        branches = [first_branch] + p4

        # Return the case expression.
        out = CaseExpressionAst(p1.pos, p1, Asts.ParenthesizedExpressionAst(p2.pos, expr=p2), branches=branches)
        return out

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_case.print(printer) + " ",
            self.cond.print(printer) + " ",
            self.kw_of.print(printer) if self.kw_of else "",
            SequenceUtils.print(printer, self.branches, sep="\n")]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.cond.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        The type of the 0th branch is used. To ensure type-safety, all branches must return the same value, but this
        check is only required if the "case" expression is being assigned to a variable (ie the return type is
        required). Also, an "else" branch is required in-case the other branches don't execute. If there are no
        branches, the return type is Void (which will be an error in the caller function).

        .. todo::
            don't require "else" for exhaustive variant destructure.
            checking for an "else" branch will error for 0-branch case expressions.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The type of the case expression.

        :raise SemanticErrors.CaseBranchesConflictingTypesError: This exception is thrown if a branch's return type
            doesn't match the first branch's return type.
        :raise SemanticErrors.CaseBranchesMissingElseBranchError: This exception is thrown if the case expression
            doesn't have an "else" block.
        """

        # The checks here only apply when assigning from this expression.
        branch_types = [b.infer_type(sm, **kwargs) for b in self.branches]
        master_branch_type = branch_types[0]

        # Pre-provided type for assignment (like a variant type).
        if lhs_type := kwargs.get("assignment_type", None):
            master_branch_type = lhs_type

        # If there is a variant branch, use the most variant type as the master branch type.
        elif variant_branch_types := [b for b in branch_types if AstTypeUtils.is_type_variant(b, sm.current_scope)]:
            most_inner_types = 0
            for variant_type in variant_branch_types:
                internal_types = variant_type.type_parts[-1].generic_argument_group["Variants"].value.type_parts[-1].generic_argument_group.arguments
                if len(internal_types) > most_inner_types:
                    master_branch_type, most_inner_types = variant_type, len(internal_types)
            branch_types.remove(master_branch_type)

        # Otherwise, if there are no variants, then the first branch type is the master branch type.
        else:
            branch_types.remove(master_branch_type)

        # Check all branches match the master branch type.
        if mismatch := [b for b in branch_types if not AstTypeUtils.symbolic_eq(master_branch_type, b, sm.current_scope, sm.current_scope)]:
            raise SemanticErrors.CaseBranchesConflictingTypesError().add(
                master_branch_type, mismatch[0]).scopes(sm.current_scope)

        # Ensure there is an "else" branch if the branches are not exhaustive.
        # Todo: need to investigate how to detect exhaustion.
        if type(self.branches[-1].patterns[0]) is not Asts.PatternVariantElseAst and not kwargs.pop("ignore_else", False):
            raise SemanticErrors.CaseBranchesMissingElseBranchError().add(
                self.cond, self.branches[-1]).scopes(sm.current_scope)

        # Return the branches' return type, if there are any branches, otherwise Void.
        if len(self.branches) > 0:
            return master_branch_type
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        The case expression requires complex semantic analysis, to ensure that all control paths are consistent over a
        number of memory-related symbolic attributes. For each control path, if a symbol has a different final
        initialization, move, partial move or pinning status, then it is marked with a special value. Then, if that
        symbol is used after the case block, an error is thrown for inconsistent memory status. This is to ensure that
        the memory status of a symbol is consistent across all control paths.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: None.

        :raise SemanticErrors.ExpressionTypeInvalidError: This exception is raised if an expression for a value is
            syntactically valid but makes no sense in this context (".." or a type).
        :raise SemanticErrors.CaseBranchMultipleDestructurePatternsError: This exception is raised if a destructure
            branch has a multi-pattern match on it (only expression comparison can use multi-pattern match).
        :raise SemanticErrors.CaseBranchesElseBranchNotLastError: This exception is raised if an "else" branch is found
            but isn't the last branch.
        """

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the condition.
        if isinstance(self.cond, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.cond).scopes(sm.current_scope)

        # Analyse the condition (outside the new scope).
        self.cond.analyse_semantics(sm, **kwargs)

        # Create the scope for the case expression.
        sm.create_and_move_into_new_scope(f"<case-expr#{self.pos}>")

        # Analyse each branch of the case expression.
        for branch in self.branches:
            # Destructures can only use 1 pattern.
            if branch.op and branch.op.token_type == SppTokenType.KwIs and len(branch.patterns) > 1:
                raise SemanticErrors.CaseBranchMultipleDestructurePatternsError().add(branch.patterns[0], branch.patterns[1]).scopes(sm.current_scope)

            # Check the "else" branch is the final branch (also ensures there is only 1).
            if type(branch.patterns[0]) is Asts.PatternVariantElseAst and branch != self.branches[-1]:
                raise SemanticErrors.CaseBranchesElseBranchNotLastError().add(branch.patterns[0].kw_else, self.branches[-1]).scopes(sm.current_scope)

            branch.analyse_semantics(sm, cond=self.cond, **kwargs)

        # Move out of the case expression scope.
        sm.move_out_of_current_scope()

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Enforce memory integrity
        self.cond.check_memory(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(
            self.cond, self.cond, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
            check_pins=False, check_pins_linked=False, mark_moves=False, **kwargs)

        sm.move_to_next_scope()

        # Check the memory status of the symbols in the case expression.
        symbol_mem_info = defaultdict(list[tuple[Asts.CaseExpressionBranchAst, LightweightMemoryInfo]])
        for branch in self.branches:
            # Make a record of the symbols' memory status in the scope before the branch is analysed.
            var_symbols_in_scope = [s for s in sm.current_scope.all_symbols() if type(s) is VariableSymbol]
            old_symbol_mem_info = {s: s.memory_info.snapshot() for s in var_symbols_in_scope}
            branch.check_memory(sm, cond=self.cond, **kwargs)
            new_symbol_mem_info = {s: s.memory_info.snapshot() for s in var_symbols_in_scope}

            # Reset the memory status of the symbols for the next branch to be analysed in the same state.
            for symbol, old_memory_status in old_symbol_mem_info.items():
                symbol.memory_info.ast_initialization = old_memory_status.ast_initialization
                symbol.memory_info.ast_moved = old_memory_status.ast_moved
                symbol.memory_info.ast_partial_moves = old_memory_status.ast_partial_moves
                symbol.memory_info.ast_pins = old_memory_status.ast_pins
                symbol.memory_info.initialization_counter = old_memory_status.initialization_counter

                # Insert or append the new memory status of the symbol.
                symbol_mem_info[symbol].append((branch, new_symbol_mem_info[symbol]))

        # Update the memory status of the symbols.
        for symbol, new_memory_info_list in symbol_mem_info.items():
            first_branch = self.branches[0]
            first_memory_info_list = new_memory_info_list[0][1]

            # Assuming all new memory states are consistent across branches, update to the first "new" state list.
            symbol.memory_info.ast_initialization = first_memory_info_list.ast_initialization
            symbol.memory_info.ast_moved = first_memory_info_list.ast_moved
            symbol.memory_info.ast_partial_moves = first_memory_info_list.ast_partial_moves
            symbol.memory_info.ast_pins = first_memory_info_list.ast_pins

            # Check the new memory status for each symbol is consistent across all branches.
            for branch, memory_info_list in new_memory_info_list[1:]:

                # Check for consistent initialization.
                if (first_memory_info_list.ast_initialization is None) is not (memory_info_list.ast_initialization is None):
                    symbol.memory_info.is_inconsistently_initialized = (
                        (first_branch, first_memory_info_list.ast_initialization),
                        (branch, memory_info_list.ast_initialization))

                # Check for consistent movement.
                if (first_memory_info_list.ast_moved is None) is not (memory_info_list.ast_moved is None):
                    symbol.memory_info.is_inconsistently_moved = (
                        (first_branch, first_memory_info_list.ast_moved),
                        (branch, memory_info_list.ast_moved))

                # Check for consistent partial movement.
                if first_memory_info_list.ast_partial_moves != memory_info_list.ast_partial_moves:
                    symbol.memory_info.is_inconsistently_partially_moved = (
                        (first_branch, first_memory_info_list.ast_partial_moves),
                        (branch, memory_info_list.ast_partial_moves))

                # Check for consistent pinning.
                if first_memory_info_list.ast_pins != memory_info_list.ast_pins:
                    symbol.memory_info.is_inconsistently_pinned = (
                        (first_branch, first_memory_info_list.ast_pins),
                        (branch, memory_info_list.ast_pins))

        # Move out of the case expression scope.
        sm.move_out_of_current_scope()

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        """
        The conditional branching is implemented as a series of LLVM conditional jumps. HTe condition is an LLVM
        translation of the AST's condition, and the branches are translated and then inserted, with fragment combination
        for the pattern matching.

        :param sm: The scope manager.
        :param llvm_module: The LLVM module to generate code into.
        :param kwargs: Additional keyword arguments.
        :return: The LLVM code for the case expression.
        """

        # Create the blocks (1 for each branch).
        llvm_blocks = []
        for i, branch in enumerate(self.branches):
            # Generate the LLVM code for the branch.
            llvm_blocks.append(kwargs["func"].append_basic_block(name=f"case_{id(self)}_branch_{i}"))

        # Add the "exit" block at the end of the case expression.
        llvm_blocks.append(kwargs["func"].append_basic_block(name=f"case_{id(self)}_exit"))

        for branch in self.branches:
            # Any "is" branches will only have 1 pattern, so no need to combine.
            if branch.op.token_type == SppTokenType.KwIs:
                # TODO
                continue

            # Otherwise, combine all the pattern conversions with binary "OR" operations (reduction).
            combined_condition = reduce(
                lambda x, y: Asts.BinaryExpressionAst(self.pos, x, Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwOr), y),
                self._binary_pattern_conversions[id(branch)][1:], self._binary_pattern_conversions[id(branch)][0])
            llvm_condition = combined_condition.code_gen_pass_2(sm, llvm_module, **kwargs)

            # Add the condition to the first block.
            # Todo

            # Create the LLVM code for the branch.
            this_branch = llvm_blocks[self.branches.index(branch)]
            if branch is not self.branches[-1]:
                next_branch = llvm_blocks[self.branches.index(branch) + 1]
                kwargs["builder"].cbranch(llvm_condition, this_branch, next_branch)

            # Position the builder in the branch block.
            kwargs["builder"].position_at_end(this_branch)

            # Add the body of the branch, then unconditionally branch to the exit block.
            llvm_body = branch.code_gen_pass_2(sm, llvm_module, **kwargs)
            kwargs["builder"].branch(llvm_blocks[-1])

        # Position the builder at the exit block.
        kwargs["builder"].position_at_end(llvm_blocks[-1])

        # Handle assignments where this is the RHS of the expression. Use "phi" to select a result.
        # Todo


__all__ = [
    "CaseExpressionAst"]
