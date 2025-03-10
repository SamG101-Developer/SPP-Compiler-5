from __future__ import annotations

import functools
from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LocalVariableDestructureObjectAst(Ast, VariableNameExtraction):
    class_type: Asts.TypeAst = field(default=None)
    tok_left_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftParenthesis))
    elements: Seq[Asts.LocalVariableNestedForDestructureObjectAst] = field(default_factory=Seq)
    tok_right_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightParenthesis))

    def __post_init__(self) -> None:
        assert self.class_type

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.tok_left_paren.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @functools.cached_property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.elements.map(lambda e: e.extract_names).flat()

    @functools.cached_property
    def extract_name(self) -> Asts.IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        return IdentifierAst(self.pos, "_Unmatchable")

    def analyse_semantics(self, scope_manager: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:

        # Analyse the class and determine the attributes of the class.
        self.class_type.analyse_semantics(scope_manager, **kwargs)
        attributes = scope_manager.current_scope.get_symbol(self.class_type).type.body.members

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = self.elements.filter_to_type(Asts.LocalVariableDestructureSkipNArgumentsAst)
        if multi_arg_skips.length > 1:
            raise SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError().add(multi_arg_skips[0], multi_arg_skips[1]).scopes(scope_manager.current_scope)

        # Multi-skip cannot contain a binding for object destructuring.
        if multi_arg_skips and multi_arg_skips[0].binding:
            raise SemanticErrors.VariableObjectDestructureWithBoundMultiSkipError().add(self, multi_arg_skips[0]).scopes(scope_manager.current_scope)

        # Create expanded "let" statements for each part of the destructure.
        for element in self.elements:
            if isinstance(element, Asts.LocalVariableDestructureSkipNArgumentsAst):
                continue

            elif isinstance(element, Asts.LocalVariableSingleIdentifierAst):
                new_ast = AstMutation.inject_code(f"let {element} = {value}.{element.name}", SppParser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)

            elif isinstance(element, Asts.LocalVariableAttributeBindingAst) and isinstance(element.value, Asts.LocalVariableSingleIdentifierAst):
                continue

            elif isinstance(element, Asts.LocalVariableAttributeBindingAst):
                new_ast = AstMutation.inject_code(f"let {element.value} = {value}.{element.name}", SppParser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)

        # Check for any missing attributes in the destructure, unless a multi-skip is present.
        if not multi_arg_skips:
            assigned_attributes = self.elements.filter_not_type(Asts.LocalVariableDestructureSkipNArgumentsAst).map(lambda e: e.name)
            missing_attributes = attributes.filter(lambda a: a.name not in assigned_attributes)
            if missing_attributes:
                raise SemanticErrors.ArgumentRequiredNameMissingError().add(self, missing_attributes[0], "attribute", "destructure argument").scopes(scope_manager.current_scope)


__all__ = ["LocalVariableDestructureObjectAst"]
