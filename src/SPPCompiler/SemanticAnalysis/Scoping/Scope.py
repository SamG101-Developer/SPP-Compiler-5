from __future__ import annotations
from typing import Any, Optional, Tuple, TYPE_CHECKING
import copy

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ClassPrototypeAst import ClassPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionAst import PostfixExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeAst import SupPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
    from SPPCompiler.SemanticAnalysis.Scoping.SymbolTable import SymbolTable
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol, VariableSymbol, Symbol


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
    _ast: Optional[FunctionPrototypeAst | ClassPrototypeAst | SupPrototypeAst]

    _direct_sup_scopes: Seq[Scope]
    _direct_sub_scopes: Seq[Scope]
    _type_symbol: Optional[TypeSymbol]

    def __init__(self, name: Any, parent: Optional[Scope] = None, *, ast: Optional[Ast] = None) -> None:
        from SPPCompiler.SemanticAnalysis.Scoping.SymbolTable import SymbolTable

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

    def __json__(self) -> dict:
        return {
            "name": self._name, "parent": self._parent.name if self._parent else "", "children": self._children, "symbol_table": self._symbol_table,
        }

    def __str__(self) -> str:
        return str(self._name)

    def add_symbol(self, symbol: Symbol) -> None:
        self._symbol_table.add(symbol)

    def all_symbols(self, exclusive: bool = False) -> Seq[Symbol]:
        # Get all the symbols in the scope.
        symbols = self._symbol_table.all()
        if not exclusive and self._parent:
            symbols.extend(self._parent.all_symbols())
        return symbols

    def has_symbol(self, name: IdentifierAst | TypeAst | GenericIdentifierAst, exclusive: bool = False) -> bool:
        return self.get_symbol(name, exclusive) is not None

    def get_symbol(self, name: IdentifierAst | TypeAst | GenericIdentifierAst, exclusive: bool = False, ignore_alias: bool = False) -> Optional[Symbol]:
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst

        # Ensure the name is a valid type.
        if not isinstance(name, (IdentifierAst, TypeAst, GenericIdentifierAst)):
            raise Exception(f"Invalid name type: {name} ({type(name)})")

        # Get the symbol from the symbol table if it exists.
        scope = self
        if isinstance(name, TypeAst):
            scope, name = shift_scope_for_namespaced_type(self, name)
        symbol = scope._symbol_table.get(name)

        # If this is not an exclusive search, search the parent scope.
        if not symbol and scope._parent and not exclusive:
            symbol = scope._parent.get_symbol(name, ignore_alias=ignore_alias)

        # If either a variable or "$" type is being searched for, search the super scopes.
        if not symbol and (isinstance(name, IdentifierAst) or name.value.startswith("$")):
            symbol = search_super_scopes(scope, name)

        # Handle any possible type aliases; sometimes the original type needs to be retrieved.
        return confirm_type_with_alias(scope, symbol, ignore_alias)

    def get_multiple_symbols(self, name: IdentifierAst, original_scope: Scope = None) -> Seq[Tuple[Symbol, Scope, int]]:
        # Get all the symbols with the given name (ambiguity checks, function overloads etc), and their "depth".
        symbols = Seq([(self._symbol_table.get(name), self, self.depth_difference(original_scope or self))])
        symbols.extend(search_super_scopes_multiple(original_scope or self, self, name))
        return symbols

    def get_variable_symbol_outermost_part(self, name: IdentifierAst | PostfixExpressionAst) -> Optional[VariableSymbol]:
        # There is no symbol for non-identifiers.
        from SPPCompiler.SemanticAnalysis import PostfixExpressionAst, PostfixExpressionOperatorMemberAccessAst

        # Define a helper lambda that validates a postfix expression.
        is_valid_postfix = lambda p: all([
            isinstance(p, PostfixExpressionAst),
            isinstance(p.op, PostfixExpressionOperatorMemberAccessAst),
            p.op.is_runtime_access()])

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
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        return self.ancestors.filter(lambda s: isinstance(s.name, IdentifierAst))[0]

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


def shift_scope_for_namespaced_type(scope: Scope, type: TypeAst) -> Tuple[Scope, GenericIdentifierAst]:
    # For TypeAsts, move through each namespace/type part accessing the namespace scope.#
    for part in type.namespace + type.types[:-1]:
        # Get the next type/namespace symbol from the scope.
        inner_symbol = scope.get_symbol(part)
        match inner_symbol:
            case None: break
            case _: scope = inner_symbol.scope
    type = type.types[-1]
    return scope, type


def search_super_scopes(scope: Scope, name: IdentifierAst | GenericIdentifierAst) -> Optional[VariableSymbol]:
    # Recursively search the super scopes for a variable symbol.
    symbol = None
    for super_scope in scope._direct_sup_scopes:
        symbol = super_scope.get_symbol(name)
        if symbol: break
    return symbol


def search_super_scopes_multiple(original_scope: Scope, scope: Scope, name: IdentifierAst) -> Seq[Tuple[VariableSymbol, Scope, int]]:
    # Recursively search the super scopes for variable symbols with the given name.
    symbols = Seq()
    for super_scope in scope._direct_sup_scopes:
        new_symbols = super_scope.get_multiple_symbols(name, original_scope)
        symbols.extend(new_symbols)
    return symbols


def confirm_type_with_alias(scope: Scope, symbol: Symbol, ignore_alias: bool) -> Optional[Symbol]:
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol

    # Get the alias symbol's old type if aliases are being ignored.
    match symbol:
        case AliasSymbol() if symbol.old_type and not ignore_alias: return scope.get_symbol(symbol.old_type)
        case _: return symbol


"""
get attribute symbol:

    scope, rhs = self, name.op.attribute
    while is_valid_postfix(name):
        scope = scope.get_variable_symbol(name.lhs).scope
        name = name.lhs
    symbol = scope.get_variable_symbol(rhs)
"""