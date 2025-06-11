from __future__ import annotations

from typing import Any, DefaultDict, Dict, Iterator, List, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter
from SPPCompiler.Utils.Progress import Progress
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class ScopeManager:
    _global_scope: Scope
    _current_scope: Scope
    _iterator: Iterator[Scope]
    normal_sup_blocks: DefaultDict[TypeSymbol, List[Scope]]
    generic_sup_blocks: Dict[TypeSymbol, Scope]

    def __init__(self, global_scope, current_scope: Optional[Scope] = None, nsbs=None, gsbs=None) -> None:
        # Create the default global and current scopes if they are not provided.
        self._global_scope = global_scope
        self._current_scope = current_scope or self._global_scope
        self._iterator = iter(self)
        self.normal_sup_blocks = nsbs or DefaultDict(list)
        self.generic_sup_blocks = gsbs or DefaultDict(list)

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

        # Return the new current scope.
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

    def attach_super_scopes(self, progress: Progress, **kwargs) -> None:
        """
        The first thing to do is to identify every single "super scope". These are scopes whose "ast" is either a
        SupPrototypeExtensionAst or a SupPrototypeFunctionsAst. Store them in a dictionary, with the key being their
        "name" attribute.

        Iterate through every "top-level" scope, and identify each type scope. This is a scope whose "ast" is a
        ClassPrototypeAst. Only look inside module scopes for these (they will never be in more nested scopes). Once a
        type scope is found, compare its name against the dictionary of super scopes, using the relaxed symbolic
        comparison.

        For every match found, attach the super scope to the class scope's "_direct_up_scopes". For sup-ext blocks, also
        add the class scope for the super-class, by using "get_symbol(super_class).scope". This is required to use the
        attributes (state) of superclasses. Only add unique superclasses once.
        """

        progress.set_max(1)
        progress.next("-")

        # Ensure the scope manager is in the global scope for scope-searching.
        self.reset()
        iterator = [*iter(self)]
        for scope in iterator:
            if isinstance(scope.type_symbol, AliasSymbol):
                if scope.type_symbol.old_sym.scope:
                    self.attach_super_scope_to_target_scope(scope, scope.type_symbol.old_sym.scope._direct_sup_scopes, **kwargs)
            elif isinstance(scope.type_symbol, TypeSymbol):
                self.attach_super_scope_to_target_scope(scope, **kwargs)

        progress.finish()
        self.reset()

    def attach_super_scope_to_target_scope(
            self, scope: Scope, custom_scopes: list[Scope] = None, progress: Optional[Progress] = None,
            **kwargs) -> None:

        from SPPCompiler.SemanticAnalysis import Asts
        if str(scope.name)[0] == "$":
            return

        scope._direct_sup_scopes = []
        super_scopes = custom_scopes if custom_scopes is not None else self.normal_sup_blocks[scope._non_generic_scope.type_symbol] + list(self.generic_sup_blocks.values())

        # Iterate through all the super scopes and check if the name matches.
        for super_scope in super_scopes:
            scope_generics_dict = {}
            if not AstTypeUtils.relaxed_symbolic_eq(scope.name, super_scope._ast.name, scope, super_scope, scope_generics_dict):
                continue
            scope_generics = Asts.GenericArgumentGroupAst.from_dict(scope_generics_dict)

            tm = ScopeManager(self.global_scope, scope.type_symbol.scope_defined_in, self.normal_sup_blocks, self.generic_sup_blocks)
            new_sup_scope, new_cls_scope = AstTypeUtils.create_generic_sup_scope(tm, super_scope, scope, scope_generics, **kwargs)
            sup_symbol = new_cls_scope.type_symbol if new_cls_scope else None
            cls_symbol = scope.type_symbol

            if isinstance(super_scope._ast, Asts.SupPrototypeExtensionAst):
                super_scope._ast._check_double_inheritance(cls_symbol, sup_symbol, self)
                super_scope._ast._check_cyclic_inheritance(sup_symbol, self)

            scope._direct_sup_scopes.append(new_sup_scope)
            if new_cls_scope:
                scope._direct_sup_scopes.append(new_cls_scope)

            if isinstance(super_scope._ast, Asts.SupPrototypeAst):
                check_conflicting_type_statements(cls_symbol, self)
                check_conflicting_cmp_statements(cls_symbol, self)

        if progress:
            progress.next(str(scope.name))

    @property
    def global_scope(self) -> Scope:
        return self._global_scope

    @property
    def current_scope(self) -> Scope:
        return self._current_scope


def check_conflicting_type_statements(cls_symbol: TypeSymbol, sm: ScopeManager) -> None:
    from SPPCompiler.SemanticAnalysis import Asts

    # Prevent duplicate types by checking if the types appear in any super class (allow overrides though).
    existing_type_names = SequenceUtils.flatten([
        [m.new_type for m in s._ast.body.members if isinstance(m, Asts.SupTypeStatementAst)]
        for s in cls_symbol.scope._direct_sup_scopes
        if isinstance(s._ast, Asts.SupPrototypeAst)])

    if duplicates := SequenceUtils.duplicates(existing_type_names):
        raise SemanticErrors.IdentifierDuplicationError().add(
            duplicates[0], duplicates[1], "associated type").scopes(sm.current_scope)


def check_conflicting_cmp_statements(cls_symbol: TypeSymbol, sm: ScopeManager) -> None:
    from SPPCompiler.SemanticAnalysis import Asts

    # Prevent duplicate cmp declarations by checking if the cmp statements appear in any super class.
    existing_cmp_names = SequenceUtils.flatten([
        [m.name for m in s._ast.body.members if isinstance(m, Asts.SupCmpStatementAst) and m.type.type_parts[-1].value[0] != "$"]
        for s in cls_symbol.scope._direct_sup_scopes
        if isinstance(s._ast, Asts.SupPrototypeAst)])

    if duplicates := SequenceUtils.duplicates(existing_cmp_names):
        raise SemanticErrors.IdentifierDuplicationError().add(
            duplicates[0], duplicates[1], "associated const").scopes(sm.current_scope)


__all__ = [
    "ScopeManager"]
