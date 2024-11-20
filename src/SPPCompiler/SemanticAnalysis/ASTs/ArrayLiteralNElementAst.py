from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ArrayLiteralNElementAst(Ast, TypeInferrable, CompilerStages):
    tok_left_bracket: TokenAst
    elements: Seq[ExpressionAst]
    tok_right_bracket: TokenAst

    def __post_init__(self) -> None:
        # Convert the elements into a sequence.
        self.elements = Seq(self.elements)

    def __eq__(self, other: ArrayLiteralNElementAst) -> bool:
        # Check both ASTs are the same type and have the same elements.
        return isinstance(other, ArrayLiteralNElementAst) and self.elements == other.elements

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_bracket.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_bracket.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Create the standard "std::Arr[T, n: BigNum]" type, with generic items.
        from SPPCompiler.SemanticAnalysis import IntegerLiteralAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Create the size literal, and infer the element type.
        size = IntegerLiteralAst.from_python_literal(self.elements.length)
        element_type = self.elements[0].infer_type(scope_manager, **kwargs).type
        array_type = CommonTypes.Arr(element_type, size, self.pos)
        array_type.analyse_semantics(scope_manager, **kwargs)
        return InferredType.from_type(array_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Analyse the elements in the array.
        self.elements.for_each(lambda element: element.analyse_semantics(scope_manager, **kwargs))
        element_types = self.elements.map(lambda e: e.infer_type(scope_manager, **kwargs))

        # Check all elements have the same type as the 0th element.
        unique_types = element_types.map_attr("type").unique()
        if unique_types.length > 1:
            raise SemanticErrors.ArrayElementsDifferentTypesError().add(unique_types[0], unique_types[1])

        # Check all elements are "owned", and not "borrowed".
        borrowed_elements = self.elements.filter(lambda e: e.infer_type(scope_manager, **kwargs).convention == ConventionMovAst)
        if borrowed_elements:
            if borrow_symbol := scope_manager.current_scope.get_variable_symbol_outermost_part(borrowed_elements[0]):
                if borrow_ast := borrow_symbol.memory_info.ast_borrowed:
                    raise SemanticErrors.ArrayElementBorrowedError().add(borrowed_elements[0], borrow_ast)


__all__ = ["ArrayLiteralNElementAst"]
