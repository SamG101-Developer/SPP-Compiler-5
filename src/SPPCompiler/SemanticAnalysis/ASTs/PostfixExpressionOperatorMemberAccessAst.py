from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionOperatorMemberAccessAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_access: TokenAst
    field: IdentifierAst | TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_access.print(printer),
            self.field.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, lhs: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, VariableSymbol
        
        # Accessing static methods off of a type, such as "Str::new()".
        if isinstance(lhs, TypeAst):
            # Check static member access "::" is being used.
            if self.tok_access.token.token_type != TokenType.TkDblColon:
                ...
        
            # Check the target field exists on the type.
            if not scope_manager.current_scope.get_symbol(lhs).scope.has_symbol(self.field):
                ...
        
        # Numerical access to a tuple, such as "tuple.0".
        elif isinstance(self.field, TokenAst):
            lhs_type = lhs.infer_type(scope_manager).type
            lhs_symbol = scope_manager.current_scope.get_symbol(lhs_type)
            
            # Check the lhs isn't a generic type.
            if lhs_symbol.is_generic:
                ...
        
            # Check the lhs is a tuple (only indexable type).
            if not lhs_type.without_generics().symbolic_eq(CommonTypes.Tup(), scope_manager.current_scope):
                ...
        
            # Check the index is within the bounds of the tuple.
            if int(self.field.token.token_metadata) >= lhs_type.types[-1].generic_argument_group.arguments.length:
                ...
        
        # Accessing a regular attribute/method, such as "class.attribute".
        elif isinstance(self.field, IdentifierAst) and self.tok_access.token.token_type == TokenType.TkDot:
            lhs_type = lhs.infer_type(scope_manager).type
            lhs_symbol = scope_manager.current_scope.get_symbol(lhs_type)
            
            # Check the lhs isn't a generic type.
            if lhs_symbol.is_generic:
                ...
            
            # Check the lhs is a variable and not a namespace.
            if isinstance(lhs_symbol, NamespaceSymbol):
                ...
        
            # Check the attribute exists on the lhs.
            if not lhs_symbol.scope.has_symbol(self.field):
                ...
        
            # Check for ambiguous symbol access (unless for function call).
            if not lhs_symbol.scope.get_symbol(self.field).type.types[-1].value.startswith("$"):
                ...
        
        # Accessing a namespaced constant, such as "std::pi".
        elif isinstance(self.field, IdentifierAst) and self.tok_access.token.token_type == TokenType.TkDblColon:
            lhs_type = lhs.infer_type(scope_manager).type
            lhs_symbol = scope_manager.current_scope.get_symbol(lhs_type)
            
            # Check the lhs is a namespace and not a variable.
            if isinstance(lhs_symbol, VariableSymbol):
                ...
        
            # Check the variable exists on the lhs.
            if not namespace_scope.has_symbol(self.field):
                ...


__all__ = ["PostfixExpressionOperatorMemberAccessAst"]
