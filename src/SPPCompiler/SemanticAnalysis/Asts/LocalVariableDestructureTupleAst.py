from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LocalVariableDestructureTupleAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
    tok_l: Asts.TokenAst = field(default=None)
    elements: Seq[Asts.LocalVariableNestedForDestructureTupleAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            self.elements.print(printer, ", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.elements.map(lambda e: e.extract_names).flat()

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return Asts.IdentifierAst(self.pos, "_Unmatchable")

    def analyse_semantics(self, sm: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = self.elements.filter_to_type(Asts.LocalVariableDestructureSkipNArgumentsAst)
        if multi_arg_skips.length > 1:
            raise SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError().add(
                multi_arg_skips[0], multi_arg_skips[1]).scopes(sm.current_scope)

        # Ensure the rhs value is a tuple.
        value_type = value.infer_type(sm, **kwargs).without_generics()
        tuple_type = CommonTypesPrecompiled.EMPTY_TUPLE
        if not value_type.symbolic_eq(tuple_type, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                self, tuple_type, value, value_type).scopes(sm.current_scope)

        # Determine the number of elements in the lhs and rhs tuples.
        num_lhs_tuple_elements = self.elements.length
        num_rhs_tuple_elements = value.infer_type(sm, **kwargs).type_parts()[0].generic_argument_group.arguments.length

        # Ensure the lhs and rhs tuples have the same number of elements unless a multi-skip is present.
        if (num_lhs_tuple_elements < num_rhs_tuple_elements and not multi_arg_skips) or num_lhs_tuple_elements > num_rhs_tuple_elements:
            raise SemanticErrors.VariableTupleDestructureTupleSizeMismatchError().add(
                self, num_lhs_tuple_elements, value, num_rhs_tuple_elements).scopes(sm.current_scope)

        # For a binding ".." destructure, ie "let (a, b, ..c, d, e, f) = t", create an intermediary rhs tuple.
        if multi_arg_skips and multi_arg_skips[0].binding:
            m = self.elements.index(multi_arg_skips[0])
            indexes = [*range(m, m + num_rhs_tuple_elements - num_lhs_tuple_elements + 1)]
            new_ast = CodeInjection.inject_code(
                f"({", ".join([f"{value}.{i}" for i in indexes])})", SppParser.parse_literal_tuple,
                pos_adjust=value.pos)
            bound_multi_skip = new_ast

        # Create new indexes like [0, 1, 2, 6, 7] if elements 3->5 are skipped (and possibly bound).
        indexes  = Seq([*range(0, (self.elements.index(multi_arg_skips[0]) if multi_arg_skips else self.elements.length - 1) + 1)])
        indexes += Seq([*range(num_lhs_tuple_elements, num_rhs_tuple_elements)])

        # Create expanded "let" statements for each part of the destructure.
        for i, element in indexes.zip(self.elements):
            if isinstance(element, Asts.LocalVariableDestructureSkipNArgumentsAst) and multi_arg_skips[0].binding:
                new_ast = CodeInjection.inject_code(
                    f"let {element.binding} = {bound_multi_skip}", SppParser.parse_let_statement_initialized,
                    pos_adjust=element.pos)
                new_ast.analyse_semantics(sm, **kwargs)

            elif isinstance(element, Asts.LocalVariableDestructureSkip1ArgumentAst):
                continue

            elif isinstance(element, Asts.LocalVariableDestructureSkipNArgumentsAst):
                continue

            else:
                new_ast = CodeInjection.inject_code(
                    f"let {element} = {value}.{i}", SppParser.parse_let_statement_initialized,
                    pos_adjust=element.pos)
                new_ast.analyse_semantics(sm, **kwargs)


__all__ = [
    "LocalVariableDestructureTupleAst"]
