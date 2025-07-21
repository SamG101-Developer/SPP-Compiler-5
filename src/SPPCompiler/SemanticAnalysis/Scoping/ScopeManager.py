from __future__ import annotations

from typing import Any, DefaultDict, Iterator, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, NamespaceSymbol, TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter
from SPPCompiler.Utils.Progress import Progress
from SPPCompiler.Utils.Sequence import SequenceUtils

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class ScopeManager:
    _global_scope: Scope
    _current_scope: Scope
    _iterator: Iterator[Scope]
    normal_sup_blocks: DefaultDict[TypeSymbol, list[Scope]]
    generic_sup_blocks: dict[TypeSymbol, Scope]

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

    def get_namespaced_scope(self, namespace: list[Asts.IdentifierAst]) -> Optional[Scope]:
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

        # Ensure the scope manager is in the global scope for scope-searching.
        self.reset()
        iterator = [x for x in iter(self) if isinstance(x.type_symbol, TypeSymbol)]
        progress.set_max(len(iterator))

        for scope in iterator:
            self.attach_super_scopes_helper(scope, **kwargs)
            progress.next(str(scope.parent_module.name))

        progress.finish()
        self.reset()

    def attach_super_scopes_helper(self, scope: Scope, **kwargs) -> None:
        if isinstance(scope.type_symbol, AliasSymbol):
            if scope.type_symbol.old_sym.scope:
                old_scope = scope.type_symbol.old_sym.scope
                scopes = self.normal_sup_blocks[old_scope.type_symbol] + list(self.generic_sup_blocks.values())
                self.attach_super_scopes_to_target_scope(scope, scopes, **kwargs)

        elif isinstance(scope.type_symbol, TypeSymbol):
            non_generic_scope = scope._non_generic_scope
            scopes = self.normal_sup_blocks[non_generic_scope.type_symbol] + list(self.generic_sup_blocks.values())
            self.attach_super_scopes_to_target_scope(scope, scopes, **kwargs)

    def attach_super_scopes_to_target_scope(
            self, scope: Scope, super_scopes: list[Scope], progress: Optional[Progress] = None, **kwargs) -> None:

        from SPPCompiler.SemanticAnalysis import Asts
        if str(scope.name)[0] == "$":
            return

        scope._direct_sup_scopes = []

        # Iterate through all the super scopes and check if the name matches.
        for sup_scope in super_scopes:

            # Relaxed comparison between the two types, capturing the generics if they exist.
            scope_generics_dict = {}
            if not AstTypeUtils.relaxed_symbolic_eq(scope.type_symbol.fq_name, sup_scope._ast.name, scope.type_symbol.scope_defined_in, sup_scope, scope_generics_dict):
                continue
            scope_generics = Asts.GenericArgumentGroupAst.from_dict(scope_generics_dict)

            # Create a generic version of the super scope if needed.
            if len(scope_generics.arguments) > 0:
                external_generics = [x for x in scope.type_symbol.scope_defined_in.all_symbols() if type(x) is not NamespaceSymbol and x.is_generic]
                new_sup_scope, new_cls_scope = AstTypeUtils.create_generic_sup_scope(self, sup_scope, scope, scope_generics, external_generics, **kwargs)
                sup_symbol = new_cls_scope.type_symbol if new_cls_scope else None
            else:
                new_sup_scope = sup_scope
                new_cls_scope = scope.get_symbol(sup_scope._ast.super_class).scope if type(sup_scope._ast) is Asts.SupPrototypeExtensionAst else None
                sup_symbol = new_cls_scope.type_symbol if new_cls_scope else None
            cls_symbol = scope.type_symbol

            # Prevent double inheritance, cyclic inheritance, and self inheritance.
            # if type(sup_scope._ast) is Asts.SupPrototypeExtensionAst:
            #     sup_scope._ast._check_cyclic_extension(sup_symbol, sup_scope)
            #     sup_scope._ast._check_double_extension(cls_symbol, sup_symbol, sup_scope)
            #     sup_scope._ast._check_self_extension(cls_symbol, sup_symbol, sup_scope)

            # Register the super scope against the current scope.
            scope._direct_sup_scopes.append(new_sup_scope)

            # Register the super scope's class scope against the current scope, if it is different. The difference check
            # is to prevent generic superimpositions ie "sup [T] T ext A" from causing "sup A ext A" from happening.
            if new_cls_scope and scope.type_symbol is not new_cls_scope.type_symbol:
                scope._direct_sup_scopes.append(new_cls_scope)

            # if isinstance(sup_scope._ast, Asts.SupPrototypeAst):
            #     check_conflicting_type_statements(cls_symbol, sup_scope, self)
            #     check_conflicting_cmp_statements(cls_symbol, sup_scope, self)

        if progress:
            progress.next(str(scope.name))

    @property
    def global_scope(self) -> Scope:
        return self._global_scope

    @property
    def current_scope(self) -> Scope:
        return self._current_scope


def check_conflicting_type_statements(cls_symbol: TypeSymbol, super_scope: Scope, sm: ScopeManager) -> None:
    from SPPCompiler.SemanticAnalysis import Asts

    # Prevent duplicate types by checking if the types appear in any super class (allow overrides though).
    existing_type_names = SequenceUtils.flatten([
        [m.new_type for m in s._ast.body.members if type(m) is Asts.SupTypeStatementAst]
        for s in cls_symbol.scope._direct_sup_scopes
        if type(s._ast) is Asts.SupPrototypeExtensionAst or type(s._ast) is Asts.SupPrototypeFunctionsAst
           and AstTypeUtils.relaxed_symbolic_eq(super_scope._ast.name, s._ast.name, super_scope, s._ast._scope)])

    if duplicates := SequenceUtils.duplicates(existing_type_names):
        raise SemanticErrors.IdentifierDuplicationError().add(
            duplicates[0], duplicates[1], "associated type").scopes(sm.current_scope)


def check_conflicting_cmp_statements(cls_symbol: TypeSymbol, super_scope: Scope, sm: ScopeManager) -> None:
    from SPPCompiler.SemanticAnalysis import Asts

    # Prevent duplicate cmp declarations by checking if the cmp statements appear in any super class.
    existing_cmp_names = SequenceUtils.flatten([
        [m.name for m in s._ast.body.members if type(m) is Asts.SupCmpStatementAst and m.type.type_parts[-1].value[0] != "$"]
        for s in cls_symbol.scope._direct_sup_scopes
        if type(s._ast) is Asts.SupPrototypeExtensionAst or type(s._ast) is Asts.SupPrototypeFunctionsAst
           and AstTypeUtils.relaxed_symbolic_eq(super_scope._ast.name, s._ast.name, super_scope, s._ast._scope)])

    if duplicates := SequenceUtils.duplicates(existing_cmp_names):
        raise SemanticErrors.IdentifierDuplicationError().add(
            duplicates[0], duplicates[1], "associated const").scopes(sm.current_scope)


__all__ = [
    "ScopeManager"]
