from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableNestedForDestructureObjectAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class LocalVariableDestructureObjectAst(Ast, VariableNameExtraction, Stage4_SemanticAnalyser):
    class_type: TypeAst
    tok_left_paren: TokenAst
    elements: Seq[LocalVariableNestedForDestructureObjectAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the elements into a sequence.
        self.elements = Seq(self.elements)

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
    def extract_names(self) -> Seq[IdentifierAst]:
        return self.elements.map(lambda e: e.extract_names).flat()

    @functools.cached_property
    def extract_name(self) -> IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        return IdentifierAst(-1, "_Unmatchable")

    def analyse_semantics(self, scope_manager: ScopeManager, value: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import LocalVariableSingleIdentifierAst, LocalVariableAttributeBindingAst
        from SPPCompiler.SemanticAnalysis import LocalVariableDestructureSkipNArgumentsAst, IdentifierAst
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Analyse the class and determine the attributes of the class.
        self.class_type.analyse_semantics(scope_manager, **kwargs)
        attributes = scope_manager.current_scope.get_symbol(self.class_type).type.body.members

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = self.elements.filter_to_type(LocalVariableDestructureSkipNArgumentsAst)
        if multi_arg_skips.length > 1:
            raise AstErrors.MULTI_SKIP_N_IN_DESTRUCTURE(multi_arg_skips[0], multi_arg_skips[1])

        # Multi-skip cannot contain a binding for object destructuring.
        if multi_arg_skips and multi_arg_skips[0].binding:
            raise AstErrors.MULTI_SKIP_N_CANNOT_HAVE_BINDING(multi_arg_skips[0])

        # Create expanded "let" statements for each part of the destructure.
        for element in self.elements:
            if isinstance(element, LocalVariableDestructureSkipNArgumentsAst):
                continue

            elif isinstance(element, LocalVariableSingleIdentifierAst):
                new_ast = AstMutation.inject_code(f"let {element} = {value}.{element.name}", Parser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)

            elif isinstance(element, LocalVariableAttributeBindingAst) and isinstance(element.value, LocalVariableSingleIdentifierAst):
                continue

            elif isinstance(element, LocalVariableAttributeBindingAst):
                new_ast = AstMutation.inject_code(f"let {element.value} = {value}.{element.name}", Parser.parse_let_statement_initialized)
                new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["LocalVariableDestructureObjectAst"]
