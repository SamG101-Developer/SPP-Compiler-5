from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementNamespaceReductionBodyAst import UseStatementNamespaceReductionBodyAst


@dataclass
class UseStatementNamespaceReductionTypesMultipleAst(Ast):
    namespace: Seq[IdentifierAst]
    tok_left_brace: TokenAst
    types: Seq[UseStatementNamespaceReductionBodyAst]
    tok_right_brace: TokenAst

    def __post_init__(self) -> None:
        # Convert the namespace and types into a sequence.
        self.namespace = Seq(self.namespace)
        self.types = Seq(self.types)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.namespace.print(printer, "::") + "::" if self.namespace else "",
            self.tok_left_brace.print(printer),
            self.types.print(printer, ", "),
            self.tok_right_brace.print(printer)]
        return "".join(string)


__all__ = ["UseStatementNamespaceReductionTypesMultipleAst"]
