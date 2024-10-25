from __future__ import annotations
from typing import Any, Iterator, Optional, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class ScopeManager:
    _global_scope: Scope
    _current_scope: Scope
    _iterator: Iterator[Scope]

    def __init__(self, global_scope: Optional[Scope] = None, current_scop: Optional[Scope] = None) -> None:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        # Create the default global and current scopes if they are not provided.
        self._global_scope = global_scope or Scope(name=IdentifierAst(-1, "_global"), manager=self)
        self._current_scope = current_scop or self._global_scope
        self._iterator = iter(self)

        # Inject the "_global" namespace symbol into this scope (makes lookups orthogonal).
        global_namespace_symbol = NamespaceSymbol(name=self._global_scope.name, scope=self._global_scope)
        self._global_scope.add_symbol(global_namespace_symbol)

    def __iter__(self) -> Iterator[Scope]:
        # Iterate over the scope manager's scopes, starting from the global scope.
        def _iterator(scope: Scope) -> Iterator[Scope]:
            yield scope
            for child in scope._children:
                yield from _iterator(child)

        # Initialize the iterator with the global scope.
        return _iterator(self._global_scope)

    def reset(self, scope: Optional[Scope] = None) -> None:
        self._current_scope = scope or self._global_scope
        self._iterator = iter(self)

    def create_and_move_into_new_scope(self, name: Any, ast: Optional[Ast] = None) -> Scope:
        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope

        # Create a new scope (parent is the current scope) and move into it.
        scope = Scope(name, self._current_scope, self, ast)
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

    def get_namespaced_scope(self, namespace: Seq[IdentifierAst]) -> Optional[Scope]:
        # Find the first scope that matches the first part of the namespace.
        namespace_symbol = None
        for scope in self._current_scope.ancestors:
            namespace_symbol = scope.get_symbol(namespace[0])
            if namespace_symbol: break

        # If the namespace symbol is found, move through the namespace parts to find the scope.
        if namespace_symbol:
            scope = namespace_symbol.scope
            for part in namespace[1:]:
                namespace_symbol = scope.get_type_symbol(part)
                if not namespace_symbol: return None
                scope = namespace_symbol.scope

            return scope

    @property
    def global_scope(self) -> Scope:
        return self._global_scope

    @property
    def current_scope(self) -> Scope:
        return self._current_scope
