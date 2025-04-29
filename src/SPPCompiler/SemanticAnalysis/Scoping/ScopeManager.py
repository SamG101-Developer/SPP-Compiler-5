from __future__ import annotations

from typing import Any, Iterator, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol, SymbolType
from SPPCompiler.SyntacticAnalysis.ErrorFormatter import ErrorFormatter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class ScopeManager:
    _global_scope: Scope
    _current_scope: Scope
    _iterator: Iterator[Scope]

    def __init__(self, global_scope, current_scop: Optional[Scope] = None) -> None:
        # Create the default global and current scopes if they are not provided.
        self._global_scope = global_scope
        self._current_scope = current_scop or self._global_scope
        self._iterator = iter(self)

    def __iter__(self) -> Iterator[Scope]:
        # Iterate over the scope manager's scopes, starting from the global scope.
        def _iterator(s: Scope) -> Iterator[Scope]:
            for child in s._children:
                yield child
                yield from _iterator(child)

        # Initialize the iterator with the current scope.
        return _iterator(self._current_scope)

    def reset(self, scope: Optional[Scope] = None, iterator: Optional[Iterator[Scope]] = None) -> None:
        # Reset the scope manager to the provided/default scope and iterator.
        self._current_scope = scope or self._global_scope
        self._iterator = iterator or iter(self)

    def create_and_move_into_new_scope(self, name: Any, ast: Optional[Asts.Ast] = None, error_formatter: Optional[ErrorFormatter] = None) -> Scope:
        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope

        # Create a new scope (parent is the current scope) and move into it.
        scope = Scope(name, self._current_scope, ast=ast, error_formatter=error_formatter)
        self._current_scope._children.append(scope)

        # Set the new scope as the current scope, and advance the iterator to match.
        self._current_scope = scope
        next(self._iterator)

        # Return the new scope.
        return scope

    def move_out_of_current_scope(self) -> Scope:
        # Exit the current scope into the parent scope and return the parent scope.
        self._current_scope = self._current_scope._parent
        return self._current_scope

    def move_to_next_scope(self) -> Scope:
        # Move to the next scope in the iterator and return it.
        self._current_scope = next(self._iterator)
        return self._current_scope

    def get_namespaced_scope(self, namespace: Seq[Asts.IdentifierAst]) -> Optional[Scope]:
        # Find the first scope that matches the first part of the namespace.
        namespace_symbol = None
        namespace_symbol = self._current_scope.get_namespace_symbol(namespace[0])

        # If the namespace symbol is found, move through the namespace parts to find the scope.
        if namespace_symbol:
            scope = namespace_symbol.scope
            for part in namespace[1:]:
                namespace_symbol = scope.get_namespace_symbol(part, exclusive=True)
                if not namespace_symbol: return None
                scope = namespace_symbol.scope

            return scope
        return None

    def relink_generics(self) -> None:
        # Check every scope in the symbol table.
        for scope in self:

            # Only check type and alias symbols that are not generic (ie not the T type for Vec[T]).
            non_generic_type_symbols = [s for s in scope._symbol_table.all() if s.symbol_type is SymbolType.TypeSymbol and not s.is_generic]
            for symbol in non_generic_type_symbols:

                # Check the type is a generic implementation (ie Vec[Str]), and remove the symbol.
                if symbol.scope._non_generic_scope is not symbol.scope:
                    self.reset(symbol.scope_defined_in)

                    # Get the base symbol (Vec), to pull the super scopes from.
                    base_symbol = scope.get_symbol(symbol.name.without_generics(), ignore_alias=True)

                    # Add the substituted super scopes to the substituted symbol.
                    symbol.scope._direct_sup_scopes = AstTypeUtils.create_generic_sup_scopes(self, base_symbol.scope, symbol.scope, symbol.name.generic_argument_group)

        self.reset()

    @property
    def global_scope(self) -> Scope:
        return self._global_scope

    @property
    def current_scope(self) -> Scope:
        return self._current_scope


__all__ = [
    "ScopeManager"]
