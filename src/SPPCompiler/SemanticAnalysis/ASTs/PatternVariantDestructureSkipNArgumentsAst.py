from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantSingleIdentifierAst import PatternVariantSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class PatternVariantDestructureSkipNArgumentsAst(Ast):
    variadic_token: TokenAst
    binding: Optional[PatternVariantSingleIdentifierAst]

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variadic_token.print(printer),
            self.binding.print(printer) if self.binding is not None else ""]
        return "".join(string)


__all__ = ["PatternVariantDestructureSkipNArgumentsAst"]
