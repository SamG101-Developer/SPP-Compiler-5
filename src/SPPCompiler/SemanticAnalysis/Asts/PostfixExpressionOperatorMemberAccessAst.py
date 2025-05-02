from __future__ import annotations

import difflib
from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, VariableSymbol, SymbolType
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class PostfixExpressionOperatorMemberAccessAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_access: Asts.TokenAst = field(default=None)
    field: Asts.IdentifierAst | Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.tok_access is not None and self.field is not None

    def __eq__(self, other: PostfixExpressionOperatorMemberAccessAst) -> bool:
        return self.tok_access == other.tok_access and self.field == other.field

    @staticmethod
    def new_runtime(pos: int, new_field: Asts.IdentifierAst | Asts.TokenAst) -> PostfixExpressionOperatorMemberAccessAst:
        return PostfixExpressionOperatorMemberAccessAst(
            tok_access=Asts.TokenAst.raw(pos=pos, token_type=SppTokenType.TkDot),
            field=new_field)

    @staticmethod
    def new_static(pos: int, new_field: Asts.IdentifierAst) -> PostfixExpressionOperatorMemberAccessAst:
        return PostfixExpressionOperatorMemberAccessAst(
            tok_access=Asts.TokenAst.raw(pos=pos, token_type=SppTokenType.TkDoubleColon),
            field=new_field)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_access.print(printer),
            self.field.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.field.pos_end

    def is_runtime_access(self) -> bool:
        return self.tok_access.token_type == SppTokenType.TkDot

    def is_static_access(self) -> bool:
        return self.tok_access.token_type == SppTokenType.TkDoubleColon

    def infer_type(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # The NamespaceSymbol type check seems dumb but check hack in "elif" block beneath.
        lhs_type = lhs.infer_type(sm)
        lhs_symbol = sm.current_scope.get_symbol(lhs_type) if not isinstance(lhs_type, NamespaceSymbol) else lhs_type

        # Todo: wrap with Opt[T] for array access => Index operator to this is only for tuples anyways?
        # Numerical access -> get the nth generic argument of the tuple.
        if isinstance(self.field, Asts.TokenAst):
            element_type = AstTypeUtils.get_nth_type_of_indexable_type(sm, int(self.field.token_data), lhs_type)
            return element_type

        # Get the field symbol
        field_symbol = lhs_symbol.scope.get_symbol(self.field, exclusive=True)

        # Accessing a member from the scope by the identifier.
        if isinstance(self.field, Asts.IdentifierAst) and field_symbol.symbol_type is SymbolType.VariableSymbol:
            attribute_type = field_symbol.type
            attribute_type = lhs_symbol.scope.get_symbol(attribute_type).fq_name
            return attribute_type

        elif isinstance(self.field, Asts.IdentifierAst) and field_symbol.symbol_type is SymbolType.NamespaceSymbol:
            attribute_type = field_symbol
            return attribute_type

        raise NotImplementedError(f"Unknown member access type: {self.field} {type(self.field)}")

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:

        # Accessing static methods off of a type, such as "Str::new()".
        if isinstance(lhs, Asts.TypeAst):
            lhs_symbol = sm.current_scope.get_symbol(lhs)

            # Check static member access "::" is being used.
            if self.is_runtime_access():
                raise SemanticErrors.MemberAccessStaticOperatorExpectedError().add(
                    lhs, self.tok_access).scopes(sm.current_scope)
        
            # Check the target field exists on the type.
            if not lhs_symbol.scope.has_symbol(self.field, exclusive=True):
                alternatives = [s.name.value for s in sm.current_scope.get_symbol(lhs).scope.all_symbols()]
                closest_match = difflib.get_close_matches(self.field.value, alternatives, n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(
                    self.field, "static member", closest_match[0] if closest_match else None).scopes(sm.current_scope)
        
        # Numerical access to a tuple, such as "tuple.0".
        elif isinstance(self.field, Asts.TokenAst):
            lhs_type = lhs.infer_type(sm)
            lhs_symbol = sm.current_scope.get_symbol(lhs_type)

            # Check the lhs isn't a generic type.
            if lhs_symbol.is_generic:
                raise SemanticErrors.GenericTypeInvalidUsageError().add(
                    lhs, lhs_type, "member access").scopes(sm.current_scope)
        
            # Check the lhs is a tuple/array (the only indexable types).
            if not AstTypeUtils.is_type_indexable(lhs_type, sm.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(
                    lhs, lhs_type, self.tok_access).scopes(sm.current_scope)
        
            # Check the index is within the bounds of the tuple/array.
            if not AstTypeUtils.is_index_within_type_bound(int(self.field.token_data), lhs_type, sm.current_scope):
                raise SemanticErrors.MemberAccessIndexOutOfBoundsError().add(
                    lhs, lhs_type, self.field).scopes(sm.current_scope)
        
        # Accessing a regular attribute/method, such as "class.attribute".
        elif isinstance(self.field, Asts.IdentifierAst) and self.is_runtime_access():
            lhs_type = lhs.infer_type(sm)
            lhs_symbol = sm.current_scope.get_symbol(lhs_type)

            # Check the lhs is a variable and not a namespace.
            if lhs_symbol.symbol_type is SymbolType.NamespaceSymbol:
                raise SemanticErrors.MemberAccessStaticOperatorExpectedError().add(
                    lhs, self.tok_access).scopes(sm.current_scope)

            # Check the lhs isn't a generic type.
            if lhs_symbol.is_generic:
                raise SemanticErrors.GenericTypeInvalidUsageError().add(
                    lhs, lhs_type, "member access").scopes(sm.current_scope)
        
            # Check the attribute exists on the lhs. todo
            if not lhs_symbol.scope.has_symbol(self.field):
                alternatives = []  # lhs_symbol.scope.all_symbols().map_attr("name")
                closest_match = difflib.get_close_matches(self.field.value, alternatives, n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(
                    self.field, "runtime member", closest_match[0] if closest_match else None).scopes(sm.current_scope)
        
        # Accessing a namespaced constant, such as "std::pi".
        elif isinstance(self.field, Asts.IdentifierAst) and self.is_static_access():
            lhs_symbol = sm.current_scope.get_symbol(lhs)
            lhs_ns_symbol = sm.current_scope.get_namespace_symbol(lhs)

            # Check the lhs is a namespace and not a variable.
            if lhs_symbol is not None and lhs_symbol.symbol_type is SymbolType.VariableSymbol:
                raise SemanticErrors.MemberAccessRuntimeOperatorExpectedError().add(
                    lhs, self.tok_access).scopes(sm.current_scope)
        
            # Check the variable exists on the lhs.
            if not lhs_ns_symbol.scope.has_symbol(self.field):
                alternatives = [s.name.value for s in lhs_ns_symbol.scope.all_symbols()]
                closest_match = difflib.get_close_matches(self.field.value, alternatives, n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(
                    self.field, "namespace member", closest_match[0] if closest_match else None).scopes(sm.current_scope)


__all__ = [
    "PostfixExpressionOperatorMemberAccessAst"]
