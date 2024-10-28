from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ArrayLiteralNElementAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
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
        from SPPCompiler.SemanticAnalysis import IntegerLiteralAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Create an array type with the number of elements as the size, and the element type from the 0th element.
        size = IntegerLiteralAst.from_python_literal(self.elements.length)
        element_type = self.elements[0].infer_type(scope_manager, **kwargs).type
        array_type = CommonTypes.Arr(element_type, size, self.pos)
        return InferredType.from_type(array_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.elements.for_each(lambda element: element.analyse_semantics(scope_manager, **kwargs))


__all__ = ["ArrayLiteralNElementAst"]
