from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class FunctionCallArgumentNamedAst(Ast):
    name: IdentifierAst
    tok_assign: TokenAst
    convention: ConventionAst
    value: ExpressionAst

    def __eq__(self, other: FunctionCallArgumentNamedAst) -> bool:
        return isinstance(other, FunctionCallArgumentNamedAst) and self.name == other.name and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer) + " ",
            self.convention.print(printer) + " ",
            self.value.print(printer)]
        return "".join(string)


__all__ = ["FunctionCallArgumentNamedAst"]
