from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import difflib

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionOperatorMemberAccessAst(Ast, TypeInferrable, CompilerStages):
    tok_access: TokenAst
    field: IdentifierAst | TokenAst

    def __eq__(self, other: PostfixExpressionOperatorMemberAccessAst) -> bool:
        return self.tok_access == other.tok_access and self.field == other.field

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_access.print(printer),
            self.field.print(printer)]
        return "".join(string)

    def is_runtime_access(self) -> bool:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return self.tok_access.token.token_type == TokenType.TkDot

    def is_static_access(self) -> bool:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return self.tok_access.token.token_type == TokenType.TkDblColon

    def infer_type(self, scope_manager: ScopeManager, lhs: ExpressionAst = None, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TokenAst
        from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement

        lhs_type = lhs.infer_type(scope_manager)
        lhs_symbol = scope_manager.current_scope.get_symbol(lhs_type.type)

        # Numerical access -> get the nth generic argument of the tuple.
        if isinstance(self.field, TokenAst):
            element_type = AstTypeManagement.get_nth_type_of_indexable_type(int(self.field.token.token_metadata), lhs_type.type, scope_manager.current_scope)
            return InferredType.from_type(element_type)

        # Accessing a member from the scope by the identifier.
        elif isinstance(self.field, IdentifierAst):
            attribute_type = lhs_symbol.scope.get_symbol(self.field).type
            return InferredType.from_type(attribute_type)

    def analyse_semantics(self, scope_manager: ScopeManager, lhs: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, VariableSymbol
        
        # Accessing static methods off of a type, such as "Str::new()".
        if isinstance(lhs, TypeAst):
            lhs_symbol = scope_manager.current_scope.get_symbol(lhs)

            # Check static member access "::" is being used.
            if self.is_runtime_access():
                raise SemanticErrors.MemberAccessStaticOperatorExpectedError().add(lhs, self.tok_access)
        
            # Check the target field exists on the type.
            if not lhs_symbol.scope.has_symbol(self.field):
                alternatives = scope_manager.current_scope.get_symbol(lhs).scope.all_symbols().map_attr("name")
                closest_match = difflib.get_close_matches(self.field.value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(self.field, "static member", closest_match[0] if closest_match else None)
        
        # Numerical access to a tuple, such as "tuple.0".
        elif isinstance(self.field, TokenAst):
            lhs_type = lhs.infer_type(scope_manager).type
            lhs_symbol = scope_manager.current_scope.get_symbol(lhs_type)

            # Check the lhs isn't a generic type.
            if lhs_symbol.is_generic:
                raise SemanticErrors.GenericTypeInvalidUsageError().add(lhs, lhs_type, "member access")
        
            # Check the lhs is a tuple/array (the only indexable types).
            if not AstTypeManagement.is_type_indexable(lhs_type, scope_manager.current_scope):
                raise SemanticErrors.MemberAccessNonIndexableError().add(lhs, lhs_type, self.tok_access)
        
            # Check the index is within the bounds of the tuple/array.
            if not AstTypeManagement.is_index_within_type_bound(int(self.field.token.token_metadata), lhs_type, scope_manager.current_scope):
                raise SemanticErrors.MemberAccessIndexOutOfBoundsError().add(lhs, lhs_type, self.field)
        
        # Accessing a regular attribute/method, such as "class.attribute".
        elif isinstance(self.field, IdentifierAst) and self.is_runtime_access():
            lhs_type = lhs.infer_type(scope_manager).type
            lhs_symbol = scope_manager.current_scope.get_symbol(lhs_type)
            
            # Check the lhs is a variable and not a namespace.
            if isinstance(lhs_symbol, NamespaceSymbol):
                raise SemanticErrors.MemberAccessStaticOperatorExpectedError().add(lhs, self.tok_access)

            # Check the lhs isn't a generic type.
            if lhs_symbol.is_generic:
                raise SemanticErrors.GenericTypeInvalidUsageError().add(lhs, lhs_type, "member access")
        
            # Check the attribute exists on the lhs.
            if not lhs_symbol.scope.has_symbol(self.field):
                alternatives = lhs_symbol.scope.all_symbols().map_attr("name")
                closest_match = difflib.get_close_matches(self.field.value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(self.field, "runtime member", closest_match[0] if closest_match else None)
        
        # Accessing a namespaced constant, such as "std::pi".
        elif isinstance(self.field, IdentifierAst) and self.is_static_access():
            lhs_val_symbol = scope_manager.current_scope.get_symbol(lhs)

            # Check the lhs is a namespace and not a variable.
            if isinstance(lhs_val_symbol, VariableSymbol):
                raise SemanticErrors.MemberAccessRuntimeOperatorExpectedError().add(lhs, self.tok_access)
        
            # Check the variable exists on the lhs.
            lhs_type = lhs.infer_type(scope_manager).type
            lhs_type_symbol = scope_manager.current_scope.get_symbol(lhs_type)
            if not lhs_type_symbol.scope.has_symbol(self.field):
                alternatives = lhs_type_symbol.scope.all_symbols().map_attr("name")
                closest_match = difflib.get_close_matches(self.field.value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(self.field, "namespace member", closest_match[0] if closest_match else None)


__all__ = ["PostfixExpressionOperatorMemberAccessAst"]
