from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableNestedForDestructureTupleAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LocalVariableDestructureTupleAst(Ast, VariableNameExtraction, Stage4_SemanticAnalyser):
    tok_left_paren: TokenAst
    elements: Seq[LocalVariableNestedForDestructureTupleAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the elements into a sequence.
        self.elements = Seq(self.elements)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @functools.cached_property
    def extract_names(self) -> Seq[IdentifierAst]:
        return self.elements.map(lambda e: e.extract_names).flat()

    @functools.cached_property
    def extract_name(self) -> IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        return IdentifierAst(-1, "_Unmatchable")

    def analyse_semantics(self, scope_manager: ScopeManager, value: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import LocalVariableDestructureSkip1ArgumentAst
        from SPPCompiler.SemanticAnalysis import LocalVariableDestructureSkipNArgumentsAst
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Determine the number of elements in the lhs and rhs tuples.
        num_lhs_tuple_elements = self.elements.length
        num_rhs_tuple_elements = value.infer_type(scope_manager, **kwargs).type.types[-1].generic_argument_group.arguments.length

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = self.elements.filter_to_type(LocalVariableDestructureSkipNArgumentsAst)
        if multi_arg_skips.length > 1:
            raise AstErrors.MULTI_SKIP_N_IN_DESTRUCTURE(multi_arg_skips[0], multi_arg_skips[1])

        # Ensure the lhs and rhs tuples have the same number of elements unless a multi-skip is present.
        if num_lhs_tuple_elements < num_lhs_tuple_elements and not multi_arg_skips or num_lhs_tuple_elements > num_rhs_tuple_elements:
            raise AstErrors.TUPLE_SIZE_MISSMATCH(self, num_lhs_tuple_elements, num_rhs_tuple_elements)

        # For a binding ".." destructure, ie "let (a, ..b, c) = t", create an intermediary rhs tuple.
        if multi_arg_skips and multi_arg_skips[0].binding:
            indexes = [i - self.elements.index(multi_arg_skips[0]) for i in range(num_lhs_tuple_elements, num_rhs_tuple_elements + 1)]
            new_ast = AstMutation.inject_code(f"({", ".join([f"{value}.{i}" for i in indexes])})", Parser.parse_literal_tuple)
            bound_multi_skip = new_ast

        # Create new indexes like [0, 1, 2, 6, 7] if elements 3->5 are skipped (and possibly bound).
        indexes  = Seq([*range(0, self.elements.index(multi_arg_skips[0]) + 1)])
        indexes += Seq([*range(num_lhs_tuple_elements, num_rhs_tuple_elements)])

        # Create expanded "let" statements for each part of the destructure.
        for i, element in indexes.zip(self.elements):
            if isinstance(element, (LocalVariableDestructureSkip1ArgumentAst, LocalVariableDestructureSkipNArgumentsAst)):
                continue

            elif isinstance(element, LocalVariableDestructureSkipNArgumentsAst) and multi_arg_skips[0].binding:
                new_ast = AstMutation.inject_code(f"let {element.binding} = {bound_multi_skip}", Parser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)

            else:
                new_ast = AstMutation.inject_code(f"let {element} = {value}.{i}", Parser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["LocalVariableDestructureTupleAst"]
