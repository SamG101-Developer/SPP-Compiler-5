from dataclasses import dataclass, field
from typing import Optional, Type, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass(kw_only=True)
class MemoryInfo:
    ast_initialization: Optional[Ast] = field(default=None)  # where the memory is initialized (mut-ex with consumption)
    ast_moved: Optional[Ast] = field(default=None)  # where the memory is consumed (mut-ex with initialization)
    ast_borrowed: Optional[Ast] = field(default=None)  # where the ast is borrowed (from parameter convention)
    ast_partially_moved: Seq[Ast] = field(default_factory=Seq)  # list of partial moves (attributes)
    ast_pinned: Seq[Ast] = field(default_factory=Seq)  # list of pinned attributes (or the entire object)

    is_borrow_ref: bool = field(default=False)
    is_borrow_mut: bool = field(default=False)
    is_inconsistently_moved: bool = field(default=False)
    is_inconsistently_pinned: bool = field(default=False)

    def moved_by(self, ast: Ast) -> None:
        self.ast_moved = ast
        self.ast_initialization = None

    def initialized_by(self, ast: Ast) -> None:
        self.ast_initialization = ast
        self.ast_moved = None

    @property
    def convention(self) -> Type[ConventionAst]:
        from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionMutAst, ConventionRefAst, ConventionMovAst
        return ConventionMutAst if self.is_borrow_mut else ConventionRefAst if self.is_borrow_ref else ConventionMovAst


class AstMemoryHandler:
    @staticmethod
    def overlaps(ast_1: Ast, ast_2: Ast) -> bool:
        c1 = str(ast_1).startswith(str(ast_2))
        c2 = str(ast_2).startswith(str(ast_1))
        return c1 or c2

    @staticmethod
    def enforce_memory_integrity(
            value_ast: Ast, move_operation_ast: Ast, scope_manager: ScopeManager, check_move: bool = True,
            check_partial_move: bool = True, check_move_from_borrowed_context: bool = True,
            check_pins: bool = True, update_memory_info: bool = True) -> None:

        from SPPCompiler.SemanticAnalysis import TupleLiteralAst, ArrayLiteralNElementAst, IdentifierAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        """
        Runs a number of checks to ensure the memory integrity of an AST is maintained. This function is responsible for
        all memory safety enforcement operations, except for the law of exclusivity, which is maintained by the
        FunctionArgumentGroupAst checker, as this maintains that status of mut/ref borrows.

        Args:
            value_ast: The AST being analysed for memory integrity.
            move_operation_ast: The AST that is performing the move operation ("=" for example).
            scope_manager: The scope manager that is managing the current scope.
            check_move: If a full move is being checked for validity.
            check_partial_move: If a partial move is being checked for validity.
            check_move_from_borrowed_context: If moving an attribute out of a borrowed context is being checked.
            check_pinned_move: If moving pinned objects is being checked.
            update_memory_info: Whether to update the memory information in the symbol table.

        Returns:
            None
        """

        # For tuple and array literals, analyse each element.
        if isinstance(value_ast, (TupleLiteralAst, ArrayLiteralNElementAst)):
            function_call = lambda: AstMemoryHandler.enforce_memory_integrity(value_ast, move_operation_ast, scope_manager, update_memory_info=update_memory_info)
            value_ast.elements.for_each(function_call)
            return

        # Get the symbol representing the expression being moved.
        symbol = scope_manager.current_scope.get_variable_symbol_outermost_part(value_ast)
        copies = scope_manager.current_scope.get_symbol(symbol.type).is_copyable
        if isinstance(symbol, NamespaceSymbol):
            raise AstErrors.INVALID_TYPE_EXPRESSION(value_ast)

        # Check for "inconsistent" memory move status, from branches.
        if check_move and symbol.memory_info.is_inconsistently_moved:
            raise AstErrors.INCONSISTENTLY_INITIALIZED_MEMORY(value_ast, scope_manager)

        # Check for "inconsistent" memory pin status, from branches.
        if check_pins and symbol.memory_info.is_inconsistently_pinned:
            raise AstErrors.INCONSISTENT_PINNED_MEMORY(value_ast, scope_manager)

        # Check the symbol has not already been moved by another operation.
        if check_move and symbol.memory_info.ast_moved and isinstance(value_ast, IdentifierAst):
            raise AstErrors.USING_UNINITIALIZED_MEMORY(value_ast, symbol.memory_info.ast_moved)

        # Check the symbol doesn't have any outstanding partial moves.
        if check_partial_move and symbol.memory_info.ast_partially_moved and isinstance(value_ast, IdentifierAst):
            raise AstErrors.USING_PARTIALLY_INITIALIZED_MEMORY(value_ast, symbol.memory_info.ast_partially_moved)

        # Check there are overlapping partial moves (for an attribute move)
        if check_partial_move and symbol.memory_info.ast_partially_moved and not isinstance(value_ast, IdentifierAst):
            if overlaps := symbol.memory_info.ast_partially_moved.filter(lambda p: AstMemoryHandler.overlaps(p, value_ast)):
                raise AstErrors.USING_PARTIALLY_INITIALIZED_MEMORY(value_ast, overlaps)

        # Check the symbol is not being moved from a borrowed context (for an attribute move).
        if check_move_from_borrowed_context and symbol.memory_info.ast_borrowed and not isinstance(value_ast, IdentifierAst):
            raise AstErrors.MOVING_FROM_BORROWED_CONTEXT(value_ast, symbol.memory_info.ast_borrowed)

        # Check the symbol being moved is not pinned.
        if check_pins and symbol.memory_info.ast_pinned and not isinstance(value_ast, IdentifierAst):
            if overlaps := symbol.memory_info.ast_pinned.filter(lambda p: AstMemoryHandler.overlaps(p, value_ast)):
                raise AstErrors.MOVING_PINNED_MEMORY(value_ast, overlaps)

        # Markt the symbol as either moved or partially moved (for non-copy types).
        if update_memory_info and not copies:
            match value_ast:
                case IdentifierAst(): symbol.memory_info.moved_by(move_operation_ast)
                case _: symbol.memory_info.ast_partially_moved.append(value_ast)
