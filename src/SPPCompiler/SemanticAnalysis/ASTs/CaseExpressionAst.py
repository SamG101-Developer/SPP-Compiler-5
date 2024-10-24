from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternBlockAst import PatternBlockAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class CaseExpressionAst(Ast):
    tok_case: TokenAst
    condition: ExpressionAst
    tok_then: TokenAst
    branches: Seq[PatternBlockAst]

    def __post_init__(self) -> None:
        # Convert the branches into a sequence.
        self.branches = Seq(self.branches)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_case.print(printer) + " ",
            self.condition.print(printer) + " ",
            self.tok_then.print(printer) + "\n",
            self.branches.print(printer, "\n")]
        return "".join(string)


__all__ = ["CaseExpressionAst"]
