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
class PinStatementAst(Ast):
    tok_pin: TokenAst
    expressions: Seq[ExpressionAst]

    def __post_init__(self) -> None:
        # Convert the expressions into a sequence.
        self.expressions = Seq(self.expressions)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_pin.print(printer) + " ",
            self.expressions.print(printer, ", ")]
        return "".join(string)


__all__ = ["PinStatementAst"]
