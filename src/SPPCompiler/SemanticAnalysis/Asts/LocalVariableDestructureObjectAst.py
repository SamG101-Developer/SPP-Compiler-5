from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LocalVariableDestructureObjectAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
    class_type: Asts.TypeAst = field(default=None)
    tok_l: Asts.TokenAst = field(default=None)
    elems: Seq[Asts.LocalVariableNestedForDestructureObjectAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)
        assert self.class_type is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.tok_l.print(printer),
            self.elems.print(printer, ", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.elems.map(lambda e: e.extract_names).flat()

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return Asts.IdentifierAst(self.pos, Asts.Mixins.VariableLikeAst.UNMATCHABLE_VARIABLE)

    def analyse_semantics(self, sm: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:

        # Analyse the class and determine the attributes of the class.
        self.class_type.analyse_semantics(sm, **kwargs)
        attributes = sm.current_scope.get_symbol(self.class_type).type.body.members

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = self.elems.filter_to_type(Asts.LocalVariableDestructureSkipNArgumentsAst)
        if multi_arg_skips.length > 1:
            raise SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError().add(
                multi_arg_skips[0], multi_arg_skips[1]).scopes(sm.current_scope)

        # Multi-skip cannot contain a binding for object destructuring.
        if multi_arg_skips and multi_arg_skips[0].binding:
            raise SemanticErrors.VariableObjectDestructureWithBoundMultiSkipError().add(
                self, multi_arg_skips[0]).scopes(sm.current_scope)

        # Create expanded "let" statements for each part of the destructure.
        for element in self.elems:
            if isinstance(element, Asts.LocalVariableDestructureSkipNArgumentsAst):
                continue

            elif isinstance(element, Asts.LocalVariableSingleIdentifierAst):
                new_ast = CodeInjection.inject_code(
                    f"let {element} = {value}.{element.name}", SppParser.parse_let_statement_initialized,
                    pos_adjust=element.pos)
                new_ast.analyse_semantics(sm, **kwargs)

            elif isinstance(element, Asts.LocalVariableAttributeBindingAst) and isinstance(element.value, Asts.LocalVariableSingleIdentifierAst):
                continue

            elif isinstance(element, Asts.LocalVariableAttributeBindingAst):
                new_ast = CodeInjection.inject_code(
                    f"let {element.value} = {value}.{element.name}", SppParser.parse_let_statement_initialized,
                    pos_adjust=element.pos)
                new_ast.analyse_semantics(sm, **kwargs)

        # Check for any missing attributes in the destructure, unless a multi-skip is present.
        if not multi_arg_skips:
            assigned_attributes = self.elems.filter_not_type(Asts.LocalVariableDestructureSkipNArgumentsAst).map(lambda e: e.name)
            missing_attributes = attributes.filter(lambda a: a.name not in assigned_attributes)
            if missing_attributes:
                raise SemanticErrors.ArgumentRequiredNameMissingError().add(
                    self, missing_attributes[0], "attribute", "destructure argument").scopes(sm.current_scope)


__all__ = [
    "LocalVariableDestructureObjectAst"]
