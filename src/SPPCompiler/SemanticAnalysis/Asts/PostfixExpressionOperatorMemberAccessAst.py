from __future__ import annotations

import difflib
from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class PostfixExpressionOperatorMemberAccessAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_access: Asts.TokenAst = field(default=None)
    field: Asts.IdentifierAst | Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.tok_access is not None and self.field is not None

    def __eq__(self, other: PostfixExpressionOperatorMemberAccessAst) -> bool:
        return self.tok_access == other.tok_access and self.field == other.field

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
        lhs_type = lhs.infer_type(sm)
        lhs_symbol = sm.current_scope.get_symbol(lhs_type)

        # Todo: wrap with Opt[T] for array access => Index operator to this is only for tuples anyways?
        # Numerical access -> get the nth generic argument of the tuple.
        if isinstance(self.field, Asts.TokenAst):
            element_type = AstTypeUtils.get_nth_type_of_indexable_type(sm, int(self.field.token_data), lhs_type)
            return element_type

        # Accessing a member from the scope by the identifier.
        field_symbol = lhs_symbol.scope.get_symbol(self.field)
        if isinstance(self.field, Asts.IdentifierAst) and isinstance(field_symbol, VariableSymbol):
            attribute_type = field_symbol.type
            return attribute_type

        elif isinstance(self.field, Asts.IdentifierAst) and isinstance(field_symbol, NamespaceSymbol):
            attribute_type = field_symbol.name
            return attribute_type

        raise NotImplementedError("Unknown member access type.")

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
                alternatives = sm.current_scope.get_symbol(lhs).scope.all_symbols().map_attr("name")
                closest_match = difflib.get_close_matches(self.field.value, alternatives.map_attr("value"), n=1, cutoff=0)
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
            if isinstance(lhs_symbol, NamespaceSymbol):
                raise SemanticErrors.MemberAccessStaticOperatorExpectedError().add(
                    lhs, self.tok_access).scopes(sm.current_scope)

            # Check the lhs isn't a generic type.
            if lhs_symbol.is_generic:
                raise SemanticErrors.GenericTypeInvalidUsageError().add(
                    lhs, lhs_type, "member access").scopes(sm.current_scope)
        
            # Check the attribute exists on the lhs. todo
            if not lhs_symbol.scope.has_symbol(self.field):
                alternatives = Seq()  # lhs_symbol.scope.all_symbols().map_attr("name")
                closest_match = difflib.get_close_matches(self.field.value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(
                    self.field, "runtime member", closest_match[0] if closest_match else None).scopes(sm.current_scope)
        
        # Accessing a namespaced constant, such as "std::pi".
        elif isinstance(self.field, Asts.IdentifierAst) and self.is_static_access():
            lhs_symbol = sm.current_scope.get_symbol(lhs)
            lhs_ns_symbol = sm.current_scope.get_namespace_symbol(lhs)

            # Check the lhs is a namespace and not a variable.
            if isinstance(lhs_symbol, VariableSymbol):
                raise SemanticErrors.MemberAccessRuntimeOperatorExpectedError().add(
                    lhs, self.tok_access).scopes(sm.current_scope)
        
            # Check the variable exists on the lhs.
            if not lhs_ns_symbol.scope.has_symbol(self.field):
                alternatives = lhs_ns_symbol.scope.all_symbols().map_attr("name")
                closest_match = difflib.get_close_matches(self.field.value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(
                    self.field, "namespace member", closest_match[0] if closest_match else None).scopes(sm.current_scope)


__all__ = [
    "PostfixExpressionOperatorMemberAccessAst"]
