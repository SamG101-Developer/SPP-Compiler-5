from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableNestedForDestructureArrayAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LocalVariableDestructureArrayAst(Ast, VariableNameExtraction, CompilerStages):
    tok_left_paren: TokenAst
    elements: Seq[LocalVariableNestedForDestructureArrayAst]
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
        return IdentifierAst(self.pos, "_Unmatchable")

    def analyse_semantics(self, scope_manager: ScopeManager, value: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import LocalVariableDestructureSkip1ArgumentAst
        from SPPCompiler.SemanticAnalysis import LocalVariableDestructureSkipNArgumentsAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = self.elements.filter_to_type(LocalVariableDestructureSkipNArgumentsAst)
        if multi_arg_skips.length > 1:
            raise SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError().add(multi_arg_skips[0], multi_arg_skips[1])

        # Ensure the rhs value is a array.
        value_type = value.infer_type(scope_manager, **kwargs).without_generics()
        array_type = InferredType.from_type(CommonTypes.Arr(None, self.elements.length).without_generics())
        if not value_type.symbolic_eq(array_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self, array_type, value, value_type)

        # Determine the number of elements in the lhs and rhs arrays.
        num_lhs_array_elements = self.elements.length
        num_rhs_array_elements = int(value.infer_type(scope_manager, **kwargs).type.types[-1].generic_argument_group.arguments[1].value.value.token.token_metadata)

        # Ensure the lhs and rhs arrays have the same number of elements unless a multi-skip is present.
        if (num_lhs_array_elements < num_rhs_array_elements and not multi_arg_skips) or num_lhs_array_elements > num_rhs_array_elements:
            raise SemanticErrors.VariableArrayDestructureArraySizeMismatchError().add(self, num_lhs_array_elements, value, num_rhs_array_elements)

        # For a binding ".." destructure, ie "let (a, ..b, c) = t", create an intermediary rhs array.
        if multi_arg_skips and multi_arg_skips[0].binding:
            indexes = [i - self.elements.index(multi_arg_skips[0]) - 1 for i in range(num_lhs_array_elements, num_rhs_array_elements + 1)]
            parse_func = lambda parser: parser.parse_literal_array(parser.parse_expression)
            new_ast = AstMutation.inject_code(f"[{", ".join([f"{value}.{i}" for i in indexes])}]", parse_func)
            bound_multi_skip = new_ast

        # Create new indexes like [0, 1, 2, 6, 7] if elements 3->5 are skipped (and possibly bound).
        indexes  = Seq([*range(0, (self.elements.index(multi_arg_skips[0]) if multi_arg_skips else self.elements.length - 1) + 1)])
        indexes += Seq([*range(num_lhs_array_elements, num_rhs_array_elements)])

        # Create expanded "let" statements for each part of the destructure.
        for i, element in indexes.zip(self.elements):
            if isinstance(element, LocalVariableDestructureSkipNArgumentsAst) and multi_arg_skips[0].binding:
                new_ast = AstMutation.inject_code(f"let {element.binding} = {bound_multi_skip}", Parser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)

            elif isinstance(element, (LocalVariableDestructureSkip1ArgumentAst, LocalVariableDestructureSkipNArgumentsAst)):
                continue

            else:
                new_ast = AstMutation.inject_code(f"let {element} = {value}.{i}", Parser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["LocalVariableDestructureArrayAst"]
