from __future__ import annotations

import copy
from typing import Any, Optional, Tuple, TYPE_CHECKING

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.Compiler.ModuleTree import Module
from SPPCompiler.SemanticAnalysis.Scoping.SymbolTable import SymbolTable
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, TypeSymbol, VariableSymbol, Symbol, \
    AliasSymbol
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast


class Scope:
    """
    Attributes:
        _name: The name of the scope: TypeAst/SupFunctionsIdentifier/SupInheritanceIdentifier/str.
        _parent: The parent scope (always exists unless this is the global scope).
        _children: The children scopes.
        _symbol_table: The symbol table.
        _ast: The AST (is this is a cls/fun/sup scope).

        _direct_sup_scopes: The direct super scopes (TypeScopes).
        _direct_sub_scopes: The direct sub scopes (TypeScopes).
        _type_symbol: The type symbol (if this is a type scope).
    """

    _name: Any
    _parent: Optional[Scope]
    _children: Seq[Scope]
    _symbol_table: SymbolTable
    _ast: Optional[Asts.FunctionPrototypeAst | Asts.ClassPrototypeAst | Asts.SupPrototypeAst]

    _direct_sup_scopes: Seq[Scope]
    _direct_sub_scopes: Seq[Scope]
    _type_symbol: Optional[TypeSymbol | NamespaceSymbol]
    _non_generic_scope: Optional[Scope]

    def __init__(self, name: Any, parent: Optional[Scope] = None, *, ast: Optional[Ast] = None) -> None:
        # Initialize the scope with the given name, parent, and AST.
        self._name = name
        self._parent = parent
        self._ast = ast

        # Initialize everything else with default values.
        self._children = Seq()
        self._symbol_table = SymbolTable()
        self._direct_sup_scopes = Seq()
        self._direct_sub_scopes = Seq()
        self._type_symbol = None
        self._non_generic_scope = self

    @staticmethod
    def new_global_from_module(module: Module) -> Scope:
        # Create a new global scope.
        global_scope = Scope(name=Asts.IdentifierAst(-1, "_global"))

        # Inject the "_global" namespace symbol into this scope (makes lookups orthogonal).
        global_namespace_symbol = NamespaceSymbol(name=global_scope.name, scope=global_scope)
        global_scope.add_symbol(global_namespace_symbol)
        global_scope._type_symbol = global_namespace_symbol
        global_scope._ast = module.module_ast

        # Return the global scope.
        return global_scope

    def __json__(self) -> dict:
        return {
            "scope_name": self._name, "parent": self._parent.name if self._parent else "", "children": self._children,
            "symbol_table": self._symbol_table, "sup_scopes": [s.name for s in self._direct_sup_scopes],
            "sub_scopes": [s.name for s in self._direct_sub_scopes], "type_symbol": self._type_symbol.name if self._type_symbol else "",
        }

    def __str__(self) -> str:
        return str(self._name)

    def _translate_symbol(self, symbol: Symbol) -> Symbol:
        generic_argument_ctor = {VariableSymbol: Asts.GenericCompArgumentNamedAst, TypeSymbol: Asts.GenericTypeArgumentNamedAst}
        generics = self._symbol_table.all()
        generics = generics.map(lambda s: generic_argument_ctor[type(s)].from_symbol(s))

        new_symbol = symbol

        if isinstance(symbol, VariableSymbol):
            new_symbol = copy.deepcopy(symbol)
            new_symbol.type = symbol.type.sub_generics(generics)

        elif isinstance(symbol, TypeSymbol):
            new_fq_name = symbol.fq_name.sub_generics(generics)
            new_symbol = self._non_generic_scope.get_symbol(new_fq_name)

        return new_symbol

    def add_symbol(self, symbol: Symbol) -> None:
        if isinstance(symbol, TypeSymbol):
            assert isinstance(symbol.name, Asts.GenericIdentifierAst)
        # Add a symbol to the scope.
        self._symbol_table.add(symbol)

    def rem_symbol(self, symbol_name: Asts.IdentifierAst) -> None:
        # Remove a symbol from the scope.
        self._symbol_table.rem(symbol_name)

    def all_symbols(self, exclusive: bool = False) -> Seq[Symbol]:
        # Get all the symbols in the scope.
        symbols = self._symbol_table.all()
        if not exclusive and self._parent:
            symbols.extend(self._parent.all_symbols())

        # Translate the symbols if this is a generic scope.
        if self != self._non_generic_scope:
            symbols = symbols.map(self._translate_symbol)

        return symbols

    def has_symbol(self, name: Asts.IdentifierAst | Asts.TypeAst | Asts.GenericIdentifierAst, exclusive: bool = False) -> bool:
        return self.get_symbol(name, exclusive) is not None

    def get_symbol(self, name: Asts.IdentifierAst | Asts.TypeAst | Asts.GenericIdentifierAst, exclusive: bool = False, ignore_alias: bool = False) -> Optional[Symbol]:
        # Ensure the name is a valid type.
        if not isinstance(name, (Asts.IdentifierAst, Asts.TypeAst, Asts.GenericIdentifierAst)):
            return None

        # Handle generic translation.
        if self != self._non_generic_scope:
            return self._translate_symbol(self._non_generic_scope.get_symbol(name, exclusive, ignore_alias))

        # Get the symbol from the symbol table if it exists.
        scope = self
        if isinstance(name, Asts.TypeAst):
            scope, name = shift_scope_for_namespaced_type(self, name)
        symbol = scope._symbol_table.get(name)

        # If this is not an exclusive search, search the parent scope.
        if not symbol and scope._parent and not exclusive:
            symbol = scope._parent.get_symbol(name, ignore_alias=ignore_alias)

        # If either a variable or "$" type is being searched for, search the super scopes.
        if not symbol and (isinstance(name, Asts.IdentifierAst) or name.value[0] == "$"):
            symbol = search_super_scopes(scope, name)

        # Handle any possible type aliases; sometimes the original type needs to be retrieved.
        return confirm_type_with_alias(scope, symbol, ignore_alias)

    def get_multiple_symbols(self, name: Asts.IdentifierAst, original_scope: Scope = None) -> Seq[Tuple[Symbol, Scope, int]]:
        # Get all the symbols with the given name (ambiguity checks, function overloads etc), and their "depth".
        symbols = Seq([(self._symbol_table.get(name), self, self.depth_difference(original_scope or self))])
        symbols.extend(search_super_scopes_multiple(original_scope or self, self, name))
        return symbols

    def get_variable_symbol_outermost_part(self, name: Asts.IdentifierAst | Asts.PostfixExpressionAst) -> Optional[VariableSymbol]:
        # Define a helper lambda that validates a postfix expression.
        is_valid_postfix = lambda p: \
            isinstance(p, Asts.PostfixExpressionAst) and \
            isinstance(p.op, Asts.PostfixExpressionOperatorMemberAccessAst) and \
            p.op.is_runtime_access()

        # Shift to the leftmost identifier and get the symbol from the symbol table.
        if is_valid_postfix(name):
            while is_valid_postfix(name): name = name.lhs
            return self.get_symbol(name)

        # Identifiers or non-symbolic expressions can use the symbol table directly.
        else:
            return self.get_symbol(name)

    def depth_difference(self, scope: Scope) -> int:
        # Get the number of sup scopes between two scopes.

        def _depth_difference(source: Scope, target: Scope, depth: int) -> int:
            # Recursively get the depth difference between two scopes.
            if source == target: return depth
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

    @property
    def ancestors(self) -> Seq[Scope]:
        # Get all the ancestors, including this scope and the global scope.
        return Seq([node := self] + [node for _ in iter(lambda: node.parent, None) if (node := node.parent)])

    @property
    def parent_module(self) -> Scope:
        # Get the ancestor module scope.
        return self.ancestors.filter(lambda s: isinstance(s.name, Asts.IdentifierAst))[0]

    @property
    def children(self) -> Seq[Scope]:
        # Get the children scopes.
        return self._children

    @property
    def type_symbol(self) -> Optional[TypeSymbol]:
        # Get the optionally linked type symbol (if this is a type scope).
        return self._type_symbol

    @property
    def sup_scopes(self) -> Seq[Scope]:
        # Get all the super scopes recursively.
        all_sup_scopes = Seq()
        for sup_scope in self._direct_sup_scopes:
            all_sup_scopes.append(sup_scope)
            all_sup_scopes.extend(sup_scope.sup_scopes)
        return all_sup_scopes

    @property
    def sub_scopes(self) -> Seq[Scope]:
        # Get all the sub scopes recursively.
        all_sub_scopes = Seq()
        for sub_scope in self._direct_sub_scopes:
            all_sub_scopes.append(sub_scope)
            all_sub_scopes.extend(sub_scope.sub_scopes)
        return all_sub_scopes


def shift_scope_for_namespaced_type(scope: Scope, type: Asts.TypeAst) -> Tuple[Scope, Asts.GenericIdentifierAst]:
    # For TypeAsts, move through each namespace/type part accessing the namespace scope.#
    for part in type.fq_type_parts()[:-1]:
        # Get the next type/namespace symbol from the scope.
        inner_symbol = scope.get_symbol(part)
        match inner_symbol:
            case None: break
            case _: scope = inner_symbol.scope
    type = type.type_parts()[-1]
    return scope, type


def search_super_scopes(scope: Scope, name: Asts.IdentifierAst | Asts.GenericIdentifierAst) -> Optional[VariableSymbol]:
    # Recursively search the super scopes for a variable symbol.
    symbol = None
    for super_scope in scope._direct_sup_scopes:
        symbol = super_scope.get_symbol(name)
        if symbol: break
    return symbol


def search_super_scopes_multiple(original_scope: Scope, scope: Scope, name: Asts.IdentifierAst) -> Seq[Tuple[VariableSymbol, Scope, int]]:
    # Recursively search the super scopes for variable symbols with the given name.
    symbols = Seq()
    for super_scope in scope._direct_sup_scopes:
        new_symbols = super_scope.get_multiple_symbols(name, original_scope)
        symbols.extend(new_symbols)
    return symbols


def confirm_type_with_alias(scope: Scope, symbol: Symbol, ignore_alias: bool) -> Optional[Symbol]:
    # Get the alias symbol's old type if aliases are being ignored.
    match symbol:
        case AliasSymbol() if symbol.old_type and not ignore_alias:
            symbol = scope.get_symbol(symbol.old_type)
    return symbol
