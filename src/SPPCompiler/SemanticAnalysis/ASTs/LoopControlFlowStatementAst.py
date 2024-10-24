from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class LoopControlFlowStatementAst(Ast):
    tok_seq_exit: Seq[TokenAst]
    skip_or_expr: Optional[ExpressionAst]

    def __post_init__(self) -> None:
        # Convert the exit tokens into a sequence.
        self.tok_seq_exit = Seq(self.tok_seq_exit)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_seq_exit.print(printer, " "),
            self.skip_or_expr.print(printer) if self.skip_or_expr else ""]
        return "".join(string)


__all__ = ["LoopControlFlowStatementAst"]
