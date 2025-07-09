from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Tuple

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol


@dataclass(slots=True, kw_only=True)
class LightweightMemoryInfo:
    ast_initialization: Optional[Asts.Ast]
    ast_moved: Optional[Asts.Ast]
    ast_partial_moves: Seq[Asts.Ast]
    ast_pins: Seq[Asts.Ast]
    initialization_counter: int


@dataclass(slots=True, kw_only=True)
class MemoryInfo:
    """
    The MemoryInfo class is used to store information about the memory state of a symbol. It is used to identify
    potential memory conflicts in S++ code, and generates errors when memory conflicts are detected. There are a number
    of ASTs stored within these class instances, both for checks and reporting errors.

    The "ast_initialization" is only None when the "ast_moved" is not None, and vice versa. This is because a symbol can
    not be both existing and not existing simultaneously. If there are partial moves, then the "ast_initialization" is
    still not None, and the "ast_moved" will be None.

    Attributes:
        ast_initialization: The AST where the memory is initialized (variable, parameter, etc).
        ast_initialization_old: Tracks most recent initialization despite moves (for errors).
        ast_moved: The AST where the memory is consumed (function argument, binary expression, etc).
        ast_borrowed: The AST where the memory is marked as borrowed (from parameter convention).
        ast_partial_moves: A list of partial moves (attributes).
        ast_pins: A list of pinned attributes (or the entire object).

        is_borrow_ref: If the memory is borrowed as an immutable reference.
        is_borrow_mut: If the memory is borrowed as a mutable reference.
        ast_comptime_const: If the memory is a compile-time constant (global constant or generic constant).
        is_inconsistently_initialized: If the memory is inconsistently initialized from branches => (branch, is_initialized).
        is_inconsistently_moved: If the memory is inconsistently moved from branches => (branch, is_moved).
        is_inconsistently_partially_moved: If the memory is inconsistently partially moved from branches => (branch, is_partially_moved).
        is_inconsistently_pinned: If the memory is inconsistently pinned from branches => (branch, is_pinned).
    """

    ast_initialization: Optional[Asts.Ast] = field(default=None)
    ast_initialization_old: Optional[Asts.Ast] = field(default=None)
    ast_moved: Optional[Asts.Ast] = field(default=None)
    ast_borrowed: Optional[Asts.Ast] = field(default=None)
    ast_partial_moves: Seq[Asts.Ast] = field(default_factory=list)
    ast_pins: Seq[Asts.Ast] = field(default_factory=list)
    ast_comptime_const: Optional[Asts.ExpressionAst] = field(default=None)

    initialization_counter: int = field(default=0)
    is_borrow_mut: bool = field(default=False)
    is_borrow_ref: bool = field(default=False)

    is_inconsistently_initialized: Tuple[Tuple[Asts.CaseExpressionBranchAst, bool], Tuple[Asts.CaseExpressionBranchAst, bool]] = field(default=None)
    is_inconsistently_moved: Tuple[Tuple[Asts.CaseExpressionBranchAst, bool], Tuple[Asts.CaseExpressionBranchAst, bool]] = field(default=None)
    is_inconsistently_partially_moved: Tuple[Tuple[Asts.CaseExpressionBranchAst, bool], Tuple[Asts.CaseExpressionBranchAst, bool]] = field(default=None)
    is_inconsistently_pinned: Tuple[Tuple[Asts.CaseExpressionBranchAst, bool], Tuple[Asts.CaseExpressionBranchAst, bool]] = field(default=None)

    borrow_refers_to: Seq[Tuple[Optional[Asts.Ast], Asts.FunctionCallArgumentAst, bool, Scope]] = field(default_factory=list)

    def __copy__(self) -> MemoryInfo:
        return MemoryInfo(
            ast_initialization=self.ast_initialization,
            ast_moved=self.ast_moved,
            ast_borrowed=self.ast_borrowed,
            ast_partial_moves=self.ast_partial_moves.copy(),
            ast_pins=self.ast_pins.copy(),
            ast_comptime_const=self.ast_comptime_const,
            initialization_counter=self.initialization_counter,
            is_borrow_mut=self.is_borrow_mut,
            is_borrow_ref=self.is_borrow_ref,
            is_inconsistently_initialized=self.is_inconsistently_initialized,
            is_inconsistently_moved=self.is_inconsistently_moved,
            is_inconsistently_partially_moved=self.is_inconsistently_partially_moved,
            is_inconsistently_pinned=self.is_inconsistently_pinned,
            borrow_refers_to=self.borrow_refers_to.copy())

    def moved_by(self, ast: Asts.Ast) -> None:
        # If a symbol's contents is moved, mark the symbol as moved and non-initialized.
        self.ast_moved = ast
        self.ast_initialization = None

    def initialized_by(self, ast: Asts.Ast) -> None:
        # If a symbol's contents is initialized, mark the symbol as initialized and non-moved.
        self.ast_initialization = ast
        self.ast_initialization_old = ast
        self.ast_moved = None
        self.initialization_counter += 1

    def remove_partial_move(self, ast: Asts.Ast) -> None:
        # Remove the partial move from the list, and mark the symbol as initialized if there are no more partial moves.
        if ast in self.ast_partial_moves:
            self.ast_partial_moves.remove(ast)
            if not self.ast_partial_moves: self.initialized_by(ast)

    def snapshot(self) -> LightweightMemoryInfo:
        # Return a lightweight version of the memory info, with only the relevant attributes for consistency checks.
        return LightweightMemoryInfo(
            ast_initialization=self.ast_initialization,
            ast_moved=self.ast_moved,
            ast_partial_moves=self.ast_partial_moves.copy(),
            ast_pins=self.ast_pins.copy(),
            initialization_counter=self.initialization_counter)


class AstMemoryUtils:
    """
    The AstMemoryUtils class contains static methods for memory-related checks and analysis. The key function is to
    enforce memory integrity. There are also some convenience functions for checking if memory regions overlap by
    symbol.
    """

    @staticmethod
    def overlaps(ast_1: Asts.Ast, ast_2: Asts.Ast) -> bool:
        c1 = str(ast_1).startswith(str(ast_2))
        c2 = str(ast_2).startswith(str(ast_1))
        return c1 or c2

    @staticmethod
    def right_overlaps(ast_1: Asts.Ast, ast_2: Asts.Ast) -> bool:
        c2 = str(ast_2).startswith(str(ast_1))
        return c2

    @staticmethod
    def enforce_memory_integrity(
            value_ast: Asts.ExpressionAst, move_ast: Asts.Ast, sm: ScopeManager, check_move: bool = True,
            check_partial_move: bool = True, check_move_from_borrowed_ctx: bool = True,
            check_pins: bool = True, check_pins_linked: bool = True, mark_moves: bool = True, **kwargs) -> None:

        """
        Runs a number of checks to ensure the memory integrity of an AST is maintained. This function is responsible for
        all memory safety enforcement operations, except for the law of exclusivity, which is maintained by the
        FunctionCallArgumentGroupAst checker, as this maintains that status of mut/ref borrows.

        The consistency checks are only performed if a value is actually used after the branching; if a value isn't
        used, then it can be inconsistent across branches, as the symbol will never be analysed in this method.
        
        Note that "ast_comptime_const" is never checked, because the "pins" handle this. This is because comptime const
        variables are auto-pinned. They can be copied if they superimpose Copy.

        :param value_ast: The AST being analysed for memory integrity.
        :param move_ast: The AST that is performing the move operation ("=" for example).
        :param sm: The scope manager that is managing the current scope.
        :param check_move: If a full move is being checked for validity.
        :param check_partial_move: If a partial move is being checked for validity.
        :param check_move_from_borrowed_ctx: If moving an attribute out of a borrowed context is being checked.
        :param check_pins: If moving pinned objects is being checked.
        :param check_pins_linked: If moving objects linked to pins is being checked.
        :param mark_moves: Whether to update the memory information in the symbol table.

        :raise SemanticErrors.MemoryNotInitializedUsageError: If a symbol is used before being initialized.
        :raise SemanticErrors.MemoryPartiallyInitializedUsageError: If a symbol is used before being fully initialized.
        :raise SemanticErrors.MemoryMovedFromBorrowedContextError: If a symbol gets moved from a borrowed context.
        :raise SemanticErrors.MemoryMovedWhilstPinnedError: If a symbol gets moved whilst pinned.
        :raise SemanticErrors.MemoryMovedWhilstLinkPinnedError: If a symbol gets moved whilst linked to a pinned
        :raise SemanticErrors.MemoryInconsistentlyInitializedError: If a symbol gets inconsistently initialized in
            branches.
        :raise SemanticErrors.MemoryInconsistentlyMovedError: If a symbol gets inconsistently moved in branches.
        :raise SemanticErrors.MemoryInconsistentlyPinnedError: If a symbol gets inconsistently pinned in branches.
        """

        # Todo: coroutine returns can be borrows - check moving logic here, as the outermost part may not be symbolic.
        #  Partial moves from borrowed contexts won't be checked, as the outermost part is not symbolic, but they need
        #  to be checked.
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        # For tuple and array literals, analyse each element (recursively). This ensures that all elements are
        # memory-integral such that the entire tuple or array is memory-integral.
        if isinstance(value_ast, (Asts.TupleLiteralAst, Asts.ArrayLiteralNElementAst)):
            for e in value_ast.elems:
                AstMemoryUtils.enforce_memory_integrity(
                    e, move_ast, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
                    check_pins=True, check_pins_linked=True, mark_moves=mark_moves, **kwargs)
            return

        # Get the symbol representing the outermost part of the expression being moved. If the outermost part is
        # non-symbolic, then the expression is not a variable or attribute access to a variable. No further checks are
        # required, because the expression is guaranteed to be an initialized value (function return value or literal).
        var_scope, var_sym = sm.current_scope.get_variable_symbol_outermost_part(value_ast, get_scope=True)
        if not var_sym:
            return
        copies = sm.current_scope.get_symbol(var_sym.type).is_copyable
        partial_copies = sm.current_scope.get_symbol(value_ast.infer_type(sm, **kwargs)).is_copyable

        # An identifier that is a namespace cannot be used as an expression. As all expressions are analysed in this
        # function, the check is performed here.
        if type(var_sym) is NamespaceSymbol:
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                value_ast).scopes(sm.current_scope)

        # Check for "inconsistent" memory move status, from branches. This occurs when a symbol is moved in one branch,
        # but not in another branch. This means the memory status of the symbol cannot be guaranteed, which could cause
        # memory runtime-errors: if a symbol is used, and the branch that executed moved the value. Mitigate by raising
        # a compile-time error.
        if check_move and (m := var_sym.memory_info.is_inconsistently_moved):
            raise SemanticErrors.MemoryInconsistentlyInitializedError().add(
                value_ast, m[0], m[1], "moved").scopes(sm.current_scope)

        # Check for "inconsistent" memory initialization status, from branches. This is the same as the "move" check
        # above, but for initialization. This is when a symbol is non-initialized before the branching, and only
        # initialized in some of the branches. Using the symbol after the branching could cause a memory runtime-error,
        # if the symbol is still non-initialized.
        if check_move and (m := var_sym.memory_info.is_inconsistently_initialized):
            raise SemanticErrors.MemoryInconsistentlyInitializedError().add(
                value_ast, m[0], m[1], "initialized").scopes(sm.current_scope)

        # Check for "inconsistent" memory partial-move status, from branches. This is also the same as the above "move"
        # check, but just for partial moves. Because partial moves affect the memory status of the entire object, and
        # restrict the operations performable on it, the partial move status must also be the same across all the
        # branches.
        if check_move and (m := var_sym.memory_info.is_inconsistently_partially_moved):
            raise SemanticErrors.MemoryInconsistentlyInitializedError().add(
                value_ast, m[0], m[1], "partially moved").scopes(sm.current_scope)

        # Check for "inconsistent" memory pin status, from branches. The final consistency check is for the "pin" status
        # of objects. This is required, because if a borrow is subsequently used, say in a coroutine call, then the pin
        # status of the object must be guaranteed. As such, it must be consistent across all branches.
        if check_pins and (m := var_sym.memory_info.is_inconsistently_pinned):
            raise SemanticErrors.MemoryInconsistentlyPinnedError().add(
                value_ast, m[0], m[1]).scopes(sm.current_scope)

        # Check the symbol has not already been moved by another operation. This prevents the use-after-move error from
        # ever occurring in the code. If a value is marked as moved, then that value, nor its attributes, can be used
        # against until the outermost symbol is marked as fully initialized, (and the attribute symbol isn't marked as a
        # partial move, if it is an attribute access taking place).
        if check_move and var_sym.memory_info.ast_moved:
            raise SemanticErrors.MemoryNotInitializedUsageError().add(
                var_sym.memory_info.ast_initialization_old, value_ast, var_sym.memory_info.ast_moved, sm).scopes(sm.current_scope)

        # Check the symbol doesn't have any outstanding partial moves, in the case that the entire symbol itself is
        # being used. This means that "a" cannot be moved, or borrowed from etc, if "a.b has been moved. This guarantees
        # the fully-initialized status of symbols for memory operations involving the entire symbol.
        if check_partial_move and var_sym.memory_info.ast_partial_moves and isinstance(value_ast, Asts.IdentifierAst):
            raise SemanticErrors.MemoryPartiallyInitializedUsageError().add(
                value_ast, var_sym.memory_info.ast_partial_moves[0]).scopes(sm.current_scope)

        # Check there are overlapping partial moves, for a new partial move. This means that for "a.b.c" to be moved off
        # of "a", both "a.b" and "a.b.c.d" must not be partially moved off of "a". This guarantees that "a.b" is
        # fully-initialized when it is moved off of "a".
        if check_partial_move and var_sym.memory_info.ast_partial_moves and not isinstance(value_ast, Asts.IdentifierAst):
            if overlaps := [p for p in var_sym.memory_info.ast_partial_moves if AstMemoryUtils.right_overlaps(p, value_ast)]:
                raise SemanticErrors.MemoryNotInitializedUsageError().add(
                    var_sym.memory_info.ast_initialization_old, value_ast, overlaps[0], sm).scopes(sm.current_scope)

        # Check the symbol is not being moved from a borrowed context. This prevents partial moves off of borrowed
        # object, because the current context doesn't have ownership of the object. This guarantees that when control is
        # returned to the original context, the object is still in the same (fully-initialized) memory state as before
        # the borrow took place. todo: add "partial_copies" to tests
        if check_move_from_borrowed_ctx and var_sym.memory_info.ast_borrowed and not isinstance(value_ast, Asts.IdentifierAst) and not partial_copies:
            raise SemanticErrors.MemoryMovedFromBorrowedContextError().add(
                value_ast, var_sym.memory_info.ast_borrowed).scopes(sm.current_scope)

        # Check the symbol being moved is not pinned. This prevents pinned objects from moving memory location. Pinned
        # objects must not move location, because they might be being borrowed into a coroutine or asynchronous function
        # call.
        # Todo: partial_copies with pins?
        # Todo: at some point, "copies" will be usable as  generic constraint (not a just a concrete type)
        if not copies and var_sym.memory_info.ast_pins and (pin := var_sym.memory_info.ast_pins[0]):
            pin_sym = var_scope.get_symbol(pin)
            if check_pins_linked and var_sym is not pin_sym:
                raise SemanticErrors.MemoryMovedWhilstLinkPinnedError().add(
                    value_ast, var_sym.memory_info.ast_initialization, var_sym.memory_info.ast_pins[0], pin_sym.memory_info.ast_initialization_old).scopes(sm.current_scope)

            elif check_pins and var_sym is pin_sym:
                raise SemanticErrors.MemoryMovedWhilstPinnedError().add(
                    value_ast, var_sym.memory_info.ast_initialization, var_sym.memory_info.ast_pins[0]).scopes(sm.current_scope)

        # Mark the symbol as either moved or partially moved (for non-copy types). Entire objects are marked as moved,
        # and attribute accesses are marked as partial moves on the symbol representing the entire object. If the type
        # is copyable, then no movements are marked.
        if mark_moves and isinstance(value_ast, Asts.IdentifierAst) and not copies:
            var_sym.memory_info.moved_by(move_ast)
        elif mark_moves and not isinstance(value_ast, Asts.IdentifierAst) and not partial_copies:
            var_sym.memory_info.ast_partial_moves.append(value_ast)
