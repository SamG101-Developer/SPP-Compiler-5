from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class TupleLiteralAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_left_paren: TokenAst
    elements: Seq[ExpressionAst]
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

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Create the standard "std::Tup[..Items]" type, with generic items.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        inner_types = self.elements.map(lambda element: element.infer_type(scope_manager, **kwargs).type)
        tuple_type = CommonTypes.Tup(inner_types, self.pos)
        tuple_type.analyse_semantics(scope_manager, **kwargs)
        return InferredType.from_type(tuple_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.ASTs import ConventionMovAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Analyse the elements in the tuple.
        self.elements.for_each(lambda element: element.analyse_semantics(scope_manager, **kwargs))

        # Check all elements are "owned", and not "borrowed".
        borrowed_elements = self.elements.filter(lambda e: e.infer_type(scope_manager, **kwargs).convention == ConventionMovAst)
        if borrowed_elements:
            if borrow_symbol := scope_manager.current_scope.get_variable_symbol_outermost_part(borrowed_elements[0]):
                if borrow_ast := borrow_symbol.memory_info.ast_borrowed:
                    raise AstErrors.TUPLE_BORROWED_ELEMENT(borrowed_elements[0], borrow_ast)


__all__ = ["TupleLiteralAst"]
