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
class AssignmentStatementAst(Ast):
    lhs: Seq[ExpressionAst]
    op: TokenAst
    rhs: Seq[ExpressionAst]

    def __post_init__(self) -> None:
        # Convert the lhs and rhs into a sequence.
        self.lhs = Seq(self.lhs)
        self.rhs = Seq(self.rhs)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer) + " ",
            self.op.print(printer) + " ",
            self.rhs.print(printer)]
        return "".join(string)


__all__ = ["AssignmentStatementAst"]
