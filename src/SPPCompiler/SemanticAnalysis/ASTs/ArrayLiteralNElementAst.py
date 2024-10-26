from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class ArrayLiteralNElementAst(Ast):
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
            self.tok_right_bracket.print(printer)
        ]
        return "".join(string)


__all__ = ["ArrayLiteralNElementAst"]
