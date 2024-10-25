from __future__ import annotations
from typing import Any, Optional, Tuple, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionAst import PostfixExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
    from SPPCompiler.SemanticAnalysis.Scoping.SymbolTable import SymbolTable
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, NamespaceSymbol, TypeSymbol, VariableSymbol, Symbol
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


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
    _ast: Optional[Ast]

    _direct_sup_scopes: Seq[Scope]
    _direct_sub_scopes: Seq[Scope]
    _type_symbol: Optional[TypeSymbol]

    def __init__(self, name: Any, parent: Optional[Scope] = None, manager: Optional[ScopeManager] = None, ast: Optional[Ast] = None) -> None:
        self._name = name
        self._parent = parent
        self._children = Seq()
        self._symbol_table = SymbolTable()
        self._ast = ast
        self._direct_sup_scopes = Seq()
        self._direct_sub_scopes = Seq()
        self._type_symbol = None

    def add_type_symbol(self, symbol: Symbol) -> None:
        # Shift the scope for namespaced types and add the symbol to the correct scope.
        scope = self
        if isinstance(symbol, TypeSymbol):
            scope, symbol = shift_scope_for_namespaced_type(self, symbol)
        scope._symbol_table.add(symbol)

    def get_symbol(self, name: IdentifierAst | TypeAst | GenericIdentifierAst, exclusive: bool = False, ignore_alias: bool = False) -> Optional[Symbol]:
        # Get the symbol from the symbol table if it exists.
        if not isinstance(name, (IdentifierAst, TypeAst, GenericIdentifierAst)): return None
        symbol = self._symbol_table.get(name)

        # If this is not an exclusive search, search the parent scope.
        if not symbol and self._parent and not exclusive:
            symbol = self._parent.get_symbol(name)

        # If either a variable or "$" type is being searched for, search the super scopes.
        if not symbol and (symbol.name.value.startswith("$") or isinstance(name, IdentifierAst)):
            symbol = search_super_scopes(self, name)

        # Handle any possible type aliases; sometimes the original type needs to be retrieved.
        return confirm_type_with_alias(self, symbol, ignore_alias)

    def get_variable_symbol_outermost_part(self, name: IdentifierAst | PostfixExpressionAst) -> Optional[VariableSymbol]:
        # There is no symbol for non-identifiers.
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import PostfixExpressionAst, PostfixExpressionOperatorMemberAccessAst

        # Define a helper lambda that validates a postfix expression.
        is_valid_postfix = lambda p: all([
            isinstance(p, PostfixExpressionAst),
            isinstance(p.op, PostfixExpressionOperatorMemberAccessAst),
            p.op.tok_access.token.token_type == TokenType.TkDot])

        # Shift to the leftmost identifier and get the symbol from the symbol table.
        if is_valid_postfix(name):
            while is_valid_postfix(name): name = name.lhs
            return self.get_symbol(name)

        # Identifiers or non-symbolic expressions can use the symbol table directly.
        else:
            return self.get_symbol(name)

    def __json__(self) -> dict:
        return {
            "name": self._name, "parent": self._parent, "children": self._children, "symbol_table": self._symbol_table,
        }

    def __str__(self) -> str:
        return str(self._name)

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
        return self.ancestors.filter_to_type(IdentifierAst).first()

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
        for sup_scope, ast in self._direct_sup_scopes:
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


def shift_scope_for_namespaced_type(scope: Scope, symbol: TypeSymbol | NamespaceSymbol) -> Tuple[Scope, TypeSymbol | NamespaceSymbol]:
    from SPPCompiler.SemanticAnalysis import TypeAst

    # For TypeAsts, move through each namespace/type part accessing the namespace scope.
    if isinstance(symbol.name, TypeAst):
        for part in symbol.name.namespace + symbol.name.types[:-1]:
            # Get the next type/namespace symbol from the scope.
            inner_symbol = scope.get_type_symbol(part)
            match inner_symbol:
                case None: break
                case _: scope = inner_symbol.scope
        symbol.name = symbol.name.types[-1]
    return scope, symbol


def search_super_scopes(scope: Scope, name: IdentifierAst | GenericIdentifierAst) -> Optional[VariableSymbol]:
    # Recursively search the super scopes for a variable symbol.
    symbol = scope.get_symbol(name, exclusive=True)
    if not symbol:
        for super_scope, _ in scope._direct_sup_scopes:
            symbol = search_super_scopes(super_scope, name)
            if symbol: break
    return symbol


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