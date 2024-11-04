from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Type, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternBlockAst import PatternBlockAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol


@dataclass(kw_only=True)
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
        ast_moved: The AST where the memory is consumed (function argument, binary expression, etc).
        ast_borrowed: The AST where the memory is marked as borrowed (from parameter convention).
        ast_partially_moved: A list of partial moves (attributes).
        ast_pinned: A list of pinned attributes (or the entire object).

        is_borrow_ref: If the memory is borrowed as an immutable reference.
        is_borrow_mut: If the memory is borrowed as a mutable reference.
        ast_comptime_const: If the memory is a compile-time constant (global constant or generic constant).
        is_inconsistently_initialized: If the memory is inconsistently initialized from branches => (branch, is_initialized).
        is_inconsistently_moved: If the memory is inconsistently moved from branches => (branch, is_moved).
        is_inconsistently_partially_moved: If the memory is inconsistently partially moved from branches => (branch, is_partially_moved).
        is_inconsistently_pinned: If the memory is inconsistently pinned from branches => (branch, is_pinned).

        sym_pin_target: The symbol that this memory is pinned for (async/coroutine call etc)
    """

    ast_initialization: Optional[Ast] = field(default=None)
    ast_moved: Optional[Ast] = field(default=None)
    ast_borrowed: Optional[Ast] = field(default=None)
    ast_partially_moved: Seq[Ast] = field(default_factory=Seq)
    ast_pinned: Seq[Ast] = field(default_factory=Seq)
    ast_comptime_const: Optional[Ast] = field(default=None)

    initialization_counter: int = field(default=0, init=False)
    is_borrow_mut: bool = field(default=False)
    is_borrow_ref: bool = field(default=False)

    is_inconsistently_initialized: Tuple[Tuple[PatternBlockAst, bool], Tuple[PatternBlockAst, bool]] = field(default=False)
    is_inconsistently_moved: Tuple[Tuple[PatternBlockAst, bool], Tuple[PatternBlockAst, bool]] = field(default=False)
    is_inconsistently_partially_moved: Tuple[Tuple[PatternBlockAst, bool], Tuple[PatternBlockAst, bool]] = field(default=False)
    is_inconsistently_pinned: Tuple[Tuple[PatternBlockAst, bool], Tuple[PatternBlockAst, bool]] = field(default=False)

    sym_pin_target: Optional[VariableSymbol] = field(default=None)

    def moved_by(self, ast: Ast) -> None:
        # If a symbol's contents is moved, mark the symbol as moved and non-initialized.
        self.ast_moved = ast
        self.ast_initialization = None

    def initialized_by(self, ast: Ast) -> None:
        # If a symbol's contents is initialized, mark the symbol as initialized and non-moved.
        self.ast_initialization = ast
        self.ast_moved = None
        self.initialization_counter += 1

    def remove_partial_move(self, ast: Ast) -> None:
        # Remove the partial move from the list, and mark the symbol as initialized if there are no more partial moves.
        self.ast_partially_moved.remove(ast)
        self.ast_partially_moved.is_empty() and self.initialized_by(ast)

    @property
    def convention(self) -> Type[ConventionAst]:
        # Get the convention for the memory, based on the borrow status of the symbol.
        from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionMutAst, ConventionRefAst, ConventionMovAst
        return ConventionMutAst if self.is_borrow_mut else ConventionRefAst if self.is_borrow_ref else ConventionMovAst


class AstMemoryHandler:
    @staticmethod
    def overlaps(ast_1: Ast, ast_2: Ast) -> bool:
        c1 = str(ast_1).startswith(str(ast_2))
        c2 = str(ast_2).startswith(str(ast_1))
        return c1 or c2

    @staticmethod
    def left_overlap(ast_1: Ast, ast_2: Ast) -> bool:
        c1 = str(ast_1).startswith(str(ast_2))
        return c1

    @staticmethod
    def enforce_memory_integrity(
            value_ast: ExpressionAst, move_ast: Ast, scope_manager: ScopeManager, check_move: bool = True,
            check_partial_move: bool = True, check_move_from_borrowed_context: bool = True,
            check_pins: bool = True, update_memory_info: bool = True) -> None:

        """
        Runs a number of checks to ensure the memory integrity of an AST is maintained. This function is responsible for
        all memory safety enforcement operations, except for the law of exclusivity, which is maintained by the
        FunctionArgumentGroupAst checker, as this maintains that status of mut/ref borrows.

        Args:
            value_ast: The AST being analysed for memory integrity.
            move_ast: The AST that is performing the move operation ("=" for example).
            scope_manager: The scope manager that is managing the current scope.
            check_move: If a full move is being checked for validity.
            check_partial_move: If a partial move is being checked for validity.
            check_move_from_borrowed_context: If moving an attribute out of a borrowed context is being checked.
            check_pins: If moving pinned objects is being checked.
            update_memory_info: Whether to update the memory information in the symbol table.

        Returns:
            None
        """

        from SPPCompiler.SemanticAnalysis import TupleLiteralAst, ArrayLiteralNElementAst, IdentifierAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        # For tuple and array literals, analyse each element.
        if isinstance(value_ast, (TupleLiteralAst, ArrayLiteralNElementAst)):
            function_call = lambda v: AstMemoryHandler.enforce_memory_integrity(v, move_ast, scope_manager, update_memory_info=update_memory_info)
            value_ast.elements.for_each(function_call)
            return

        # Get the symbol representing the expression being moved.
        symbol = scope_manager.current_scope.get_variable_symbol_outermost_part(value_ast)
        if not symbol:
            return
        copies = scope_manager.current_scope.get_symbol(symbol.type).is_copyable

        # An identifier that is a namespace cannot be used as an expression.
        if isinstance(symbol, NamespaceSymbol):
            raise AstErrors.INVALID_EXPRESSION(value_ast)

        # Check for "inconsistent" memory move status, from branches.
        if check_move and (m := symbol.memory_info.is_inconsistently_moved):
            raise AstErrors.INCONSISTENTLY_INITIALIZED_MEMORY(value_ast, m[0], m[1])

        # Check for "inconsistent" memory pin status, from branches.
        if check_pins and (m := symbol.memory_info.is_inconsistently_pinned):
            raise AstErrors.INCONSISTENT_PINNED_MEMORY(value_ast, m[0], m[1])

        # Check the symbol has not already been moved by another operation.
        if check_move and symbol.memory_info.ast_moved and isinstance(value_ast, IdentifierAst):
            raise AstErrors.USING_UNINITIALIZED_MEMORY(value_ast, symbol.memory_info.ast_moved)

        # Check the symbol doesn't have any outstanding partial moves.
        if check_partial_move and symbol.memory_info.ast_partially_moved and isinstance(value_ast, IdentifierAst):
            raise AstErrors.USING_PARTIALLY_INITIALIZED_MEMORY(value_ast, symbol.memory_info.ast_partially_moved[0])

        # Check there are overlapping partial moves (for an attribute move)
        if check_partial_move and symbol.memory_info.ast_partially_moved and not isinstance(value_ast, IdentifierAst):
            if overlaps := symbol.memory_info.ast_partially_moved.filter(lambda p: AstMemoryHandler.overlaps(p, value_ast)):
                raise AstErrors.USING_PARTIALLY_INITIALIZED_MEMORY(value_ast, overlaps[0])

        # Check the symbol is not being moved from a borrowed context (for an attribute move).
        if check_move_from_borrowed_context and symbol.memory_info.ast_borrowed and not isinstance(value_ast, IdentifierAst):
            raise AstErrors.MOVING_FROM_BORROWED_CONTEXT(move_ast, symbol.memory_info.ast_borrowed)

        # Check the symbol being moved is not pinned.
        if check_pins and symbol.memory_info.ast_pinned and not isinstance(value_ast, IdentifierAst):
            if overlaps := symbol.memory_info.ast_pinned.filter(lambda p: AstMemoryHandler.overlaps(p, value_ast)):
                raise AstErrors.MOVING_PINNED_MEMORY(move_ast, overlaps[0])

        # Markt the symbol as either moved or partially moved (for non-copy types).
        if update_memory_info and not copies:
            match value_ast:
                case IdentifierAst(): symbol.memory_info.moved_by(move_ast)
                case _: symbol.memory_info.ast_partially_moved.append(value_ast)
