from __future__ import annotations

import copy
from typing import Any, Iterator, List, Optional, Tuple

from SPPCompiler.Compiler.ModuleTree import Module
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.SymbolTable import SymbolTable
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, NamespaceSymbol, Symbol, TypeSymbol, \
    VariableSymbol
from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter
from SPPCompiler.Utils.FunctionCache import FunctionCache


class Scope:
    """
    A scope is an object in a tree that holds symbols and other associated information about code within a block. Scopes
    are created for things like functions, loops, classes, etc. A scope has a parent scope (except for the top-level
    global scope, and a list of child scopes).

    The "sup scopes" are connected for type scopes (created by ClassPrototypeAsts), allowing symbol searching into
    superclasses. This allows extended classes to integrate seamlessly symbol resolution.
    """

    _name: str | Asts.IdentifierAst | Asts.TypeAst
    """
    The name of the scope. Likely to be a string, IdentifierAst or TypeAst. For classes, it will be the TypeAst
    representing the name of the class. For namespace/module scopes, it will be the IdentifierAst representing the
    name of the module. Otherwise, there will be string containing the type of the scope, ie function/loop/case etc,
    and the token position of the scope, mainly for debugging.
    """

    _parent: Optional[Scope]
    """
    The parent scope of this module. This is used to search for symbols in parent scopes if they aren't found in the
    current scope. Every scope has a [rent scope, except for the global scope which is the top level scope of the entire
    program.
    """

    _children: List[Scope]
    """
    The children scopes of a scope are the scopes that are created within this scope. A function scope will contain all
    scopes created by the statements that make up the function, and module scopes will contain all the class, function
    and superimposition scopes.
    """

    _symbol_table: SymbolTable
    """
    The symbol table is a wrapper around a dictionary of symbols, indexed by their name. This is used to store all the
    symbols created in this scope. Symbols can be added, removed, set, got and checked for existence.
    """

    _ast: Optional[Asts.FunctionPrototypeAst | Asts.ClassPrototypeAst | Asts.SupPrototypeAst]
    """
    Top level scopes, representing functions, classes, superimpositions, etc, have associated ASTs (the ast that was
    analysed to create this scope). This AST is stored as there are some analysis stages that use information from the
    AST directly.
    """

    _direct_sup_scopes: List[Scope]
    """
    If this is a type scope, representing a ClassPrototypeAst, then this scope may have super scopes attached to it.
    This allows for symbol resolution from super classes when they aren't found on the current class. Recursive
    searching of superscopes is used for the actual resolution.
    """

    _direct_sub_scopes: List[Scope]
    """
    The sub scopes are an inverse to the sup scope lists. So if B extends A, then A is a super scope of B, and B is a
    sub scope of A. This is used for access modifier checking, where protected symbols are accessible from sub types.
    """

    _type_symbol: Optional[TypeSymbol | NamespaceSymbol]
    """
    Type scopes have the associated type symbol attached to it for convenience. This is the symbol that represents the
    type in the symbol table. This is also set to the namespace symbol for module scopes.
    """

    _non_generic_scope: Optional[Scope]
    """
    Some scopes represent a generic scope such as Vec[Str]. This attribute will point to the non-specialized, base
    version of the type, like Vec[T]. This is used for symbol translation.
    """

    _error_formatter: ErrorFormatter
    """
    The error formatter for a scope is the same as the error formatter for the module that this scope is inside. Each
    module has its own error formatter, containing the tokens that make up the source code in the module. this allows
    for errors to be reported over the correct set of tokens depending on the source of the error.
    """

    def __init__(
            self, name: Any, parent: Optional[Scope] = None, *, ast: Optional[Asts.Ast] = None,
            error_formatter: Optional[ErrorFormatter] = None)\
            -> None:

        """
        Create a new scope with the given name and parent. The AST and error formatter are optional. Attributes are
        defaulted here, with the error formatter of the parent scope being used if not provided.
        :param name: The name of the scope. This is usually a string, but can be an IdentifierAst or TypeAst.
        :param parent: The parent scope that this scope was created in.
        :param ast: The optional AST for this scope. This is used for top level scopes, such as functions and classes.
        :param error_formatter: The error formatter for this scope, or None if the module error formatter is to be used.
        """

        # Initialize the scope with the given name, parent, and AST.
        self._name = name
        self._parent = parent
        self._ast = ast

        # Initialize everything else with default values.
        self._children = []
        self._symbol_table = SymbolTable()
        self._direct_sup_scopes = []
        self._direct_sub_scopes = []
        self._type_symbol = None

        # Error formatter is either new for the module scope, or inherited from the parent scope.
        self._non_generic_scope = self
        self._error_formatter = error_formatter or parent._error_formatter

    @staticmethod
    def new_global_from_module(module: Module) -> Scope:
        # Create a new global scope.
        global_scope = Scope(name=Asts.IdentifierAst(-1, "_global"), error_formatter=module.error_formatter)

        # Inject the "_global" namespace symbol into this scope (makes lookups orthogonal).
        global_namespace_symbol = NamespaceSymbol(name=global_scope.name, scope=global_scope)
        global_scope.add_symbol(global_namespace_symbol)
        global_scope._type_symbol = global_namespace_symbol
        global_scope._ast = module.module_ast

        # Return the global scope.
        return global_scope

    def __json__(self) -> dict:
        return {
            "scope_name": self._name, "id": id(self), "parent": self._parent.name if self._parent else "", "children": self._children,
            "symbol_table": self._symbol_table, "sup_scopes": [s.name for s in self._direct_sup_scopes], "sup_scopes_ids": [id(s) for s in self._direct_sup_scopes],
            "sub_scopes": [s.name for s in self._direct_sub_scopes], "type_symbol": self._type_symbol.name if self._type_symbol else "",
        }

    def __str__(self) -> str:
        return str(self._name)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: Scope) -> bool:
        return self is other

    def __copy__(self) -> Scope:
        # Create a shallow copy of the scope.
        new_scope = Scope(name=self._name, parent=self._parent, ast=self._ast, error_formatter=self._error_formatter)
        new_scope._symbol_table = self._symbol_table
        new_scope._direct_sup_scopes = self._direct_sup_scopes
        new_scope._direct_sub_scopes = self._direct_sub_scopes
        new_scope._type_symbol = self._type_symbol
        new_scope._children = self._children
        new_scope._non_generic_scope = self._non_generic_scope
        return new_scope

    @property
    def generics(self) -> List[Asts.GenericArgumentAst]:
        GenericArgumentCTor = {
            VariableSymbol: Asts.GenericCompArgumentNamedAst,
            TypeSymbol    : Asts.GenericTypeArgumentNamedAst,
            AliasSymbol   : Asts.GenericTypeArgumentNamedAst}

        return [GenericArgumentCTor[type(s)].from_symbol(s) for s in self._symbol_table.all() if s.is_generic]

    def add_symbol(self, symbol: Symbol) -> None:
        # Add a symbol to the scope.
        self._symbol_table.add(symbol)

    def rem_symbol(self, symbol_name: Asts.IdentifierAst | Asts.TypeAst | Asts.GenericIdentifierAst) -> None:
        # Remove a symbol from the scope.
        self._symbol_table.rem(symbol_name)

    def all_symbols(self, exclusive: bool = False, match_type: type = None, sup_scope_search: bool = False) -> Iterator[Symbol]:
        # Get all the symbols in the scope.
        for sym in self._symbol_table.all():
            yield sym

        if not exclusive and self._parent:
            yield from self._parent.all_symbols(exclusive=exclusive, match_type=match_type)

        if sup_scope_search:
            # Search the super scopes for symbols.
            for sup_scope in self._direct_sup_scopes:
                yield from sup_scope.all_symbols(exclusive=True, match_type=match_type)

    def has_symbol(
            self, name: Asts.IdentifierAst | Asts.TypeAst | Asts.GenericIdentifierAst, exclusive: bool = False,
            sym_type: Optional[type] = None, debug: bool = False) -> bool:

        # Get the symbol and check if it is None or not (None => not found).
        return self.get_symbol(name, exclusive, ignore_alias=True, sym_type=sym_type, debug=debug) is not None

    def get_symbol(
            self, name: Asts.IdentifierAst | Asts.TypeAst | Asts.GenericIdentifierAst, exclusive: bool = False,
            ignore_alias: bool = False, sym_type: Optional[type] = None, debug: bool = False) -> Optional[Symbol]:

        # Adjust the namespace and symbol name for namespaced typ symbols.
        scope = self
        if isinstance(name, Asts.TypeAst):
            name = name.without_conventions
            scope, name = shift_scope_for_namespaced_type(self, name)

        # Get the symbol from the symbol table if it exists, and ignore it if it is in the exclusion list.
        symbol = scope._symbol_table.get(name)
        if sym_type is not None and not isinstance(symbol, sym_type):
            symbol = None

        # If this is not an exclusive search, search the parent scope.
        if symbol is None and scope._parent and not exclusive:
            symbol = scope._parent.get_symbol(name, ignore_alias=ignore_alias, sym_type=sym_type, debug=debug)

        # If either a variable or "$" type is being searched for, search the super scopes.
        if symbol is None:
            symbol = search_super_scopes(scope, name, ignore_alias=ignore_alias, sym_type=sym_type, debug=debug)

        # Handle any possible type aliases; sometimes the original type needs to be retrieved.
        if symbol.__class__ is AliasSymbol and symbol.old_sym and not ignore_alias:
            return symbol.old_sym

        return symbol

    @FunctionCache.cache
    def get_namespace_symbol(self, name: Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.PostfixExpressionAst, exclusive: bool = False) -> Optional[Symbol]:
        symbol = None

        # For an IdentifierAst, get any identifier-named symbols from the symbol table.
        if name.__class__ is Asts.IdentifierAst:
            for symbol in self.all_symbols(exclusive=exclusive, match_type=Asts.IdentifierAst):
                if symbol.__class__ is NamespaceSymbol and symbol.name.value == name.value:
                    return symbol
            return None

        # For a GenericIdentifierAst, get any type-named symbols from the symbol table.
        elif name.__class__ is Asts.GenericIdentifierAst:
            for symbol in self.all_symbols(exclusive=exclusive, match_type=Asts.GenericIdentifierAst):
                if symbol.__class__ is TypeSymbol and symbol.name == name:
                    return symbol
            return None

        # For a PostfixExpressionAst iterate the parts.
        scope = self.get_namespace_symbol(name.lhs, exclusive=exclusive).scope
        while isinstance(name, Asts.PostfixExpressionAst) and isinstance(name.op, Asts.PostfixExpressionOperatorMemberAccessAst):
            symbol = scope.get_namespace_symbol(name := name.op.field, exclusive=exclusive)
            scope = symbol.scope
        return symbol

    def get_variable_symbol_outermost_part(
            self, name: Asts.IdentifierAst | Asts.PostfixExpressionAst) -> Optional[VariableSymbol]:

        # Define a helper lambda that validates a postfix expression.
        is_valid_postfix = lambda p: \
            isinstance(p, Asts.PostfixExpressionAst) and \
            isinstance(p.op, Asts.PostfixExpressionOperatorMemberAccessAst) and \
            p.op.is_runtime_access()

        is_semi_valid_postfix = lambda p: \
            isinstance(p, Asts.PostfixExpressionAst) and \
            isinstance(p.op, Asts.PostfixExpressionOperatorMemberAccessAst)

        # Shift to the leftmost identifier and get the symbol from the symbol table.
        prev_name = name
        if is_valid_postfix(name):
            while is_valid_postfix(name):
                prev_name = name
                name = name.lhs

            # Todo: not sure if this is needed here
            if is_semi_valid_postfix(prev_name) and not is_valid_postfix(prev_name):
                return self.get_symbol(name).scope.get_symbol(prev_name.op.field)

            return self.get_symbol(name)

        elif is_semi_valid_postfix(prev_name):
            return self.get_symbol(name.lhs).scope.get_symbol(prev_name.op.field)

        # Identifiers or non-symbolic expressions can use the symbol table directly.
        else:
            return self.get_symbol(name)

    def depth_difference(self, scope: Scope) -> int:
        # Get the number of sup scopes between two scopes.

        def _depth_difference(source: Scope, target: Scope, depth: int) -> int:
            # Recursively get the depth difference between two scopes.
            if source is target: return depth
            for sup_scope in source._direct_sup_scopes:
                if (result := _depth_difference(sup_scope, target, depth + 1)) >= 0:
                    return result
            return -1

        return _depth_difference(self, scope, 0)

    @property
    def name(self) -> Any:
        # Get the name of the scope.
        return self._name

    @property
    def parent(self) -> Optional[Scope]:
        # Get the parent scope.
        return self._parent

    @parent.setter
    def parent(self, parent: Scope) -> None:
        # Set the parent scope.
        self._parent = parent

    @FunctionCache.cache_property
    def ancestors(self) -> List[Scope]:
        # Get all the ancestors, including this scope and the global scope.
        return [node := self] + [node for _ in iter(lambda: node.parent, None) if (node := node.parent)]

    @FunctionCache.cache_property
    def parent_module(self) -> Scope:
        # Get the ancestor module scope.
        return [s for s in self.ancestors if s.name.__class__ is Asts.IdentifierAst][0]

    @property
    def children(self) -> List[Scope]:
        # Get the children scopes.
        return self._children

    @property
    def type_symbol(self) -> Optional[TypeSymbol | AliasSymbol]:
        # Get the optionally linked type symbol (if this is a type scope).
        return self._type_symbol

    @type_symbol.setter
    def type_symbol(self, symbol: TypeSymbol | AliasSymbol) -> None:
        self._type_symbol = symbol

    @property
    def sup_scopes(self) -> List[Scope]:
        # Get all the super scopes recursively.
        all_sup_scopes = []
        for sup_scope in self._direct_sup_scopes:
            all_sup_scopes.append(sup_scope)
            all_sup_scopes.extend(sup_scope.sup_scopes)
        return all_sup_scopes

    @property
    def direct_sup_types(self) -> List[Asts.TypeAst]:
        return [s.type_symbol.fq_name for s in self._direct_sup_scopes if isinstance(s._ast, Asts.ClassPrototypeAst)]

    @property
    def sup_types(self) -> List[Asts.TypeAst]:
        return [s.type_symbol.fq_name for s in self.sup_scopes if isinstance(s._ast, Asts.ClassPrototypeAst)]

    @property
    def sub_scopes(self) -> List[Scope]:
        # Get all the sub scopes recursively.
        all_sub_scopes = []
        for sub_scope in self._direct_sub_scopes:
            all_sub_scopes.append(sub_scope)
            all_sub_scopes.extend(sub_scope.sub_scopes)
        return all_sub_scopes


def shift_scope_for_namespaced_type(scope: Scope, type: Asts.TypeAst) -> Tuple[Scope, Asts.GenericIdentifierAst]:
    # For TypeAsts, move through each namespace/type part accessing the namespace scope.
    for part in type.fq_type_parts[:-1]:
        # Get the next type/namespace symbol from the scope.
        inner_symbol = scope.get_namespace_symbol(part) if part.__class__ is Asts.IdentifierAst else scope.get_symbol(part)
        match inner_symbol:
            case None: break
            case _: scope = inner_symbol.scope
    type = type.type_parts[-1]
    return scope, type


def search_super_scopes(
        scope: Scope, name: Asts.IdentifierAst | Asts.GenericIdentifierAst,
        ignore_alias: bool, sym_type: Optional[type] = None, debug: bool = False) -> Optional[Symbol]:

    # Recursively search the super scopes for a variable symbol.
    symbol = None
    for super_scope in scope._direct_sup_scopes:
        symbol = super_scope.get_symbol(name, exclusive=True, ignore_alias=ignore_alias, sym_type=sym_type, debug=debug)
        if symbol: break
    return symbol


__all__ = [
    "Scope"]
