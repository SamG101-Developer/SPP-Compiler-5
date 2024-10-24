from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableSingleIdentifierAst import LocalVariableSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class LocalVariableDestructureSkipNArgumentsAst(Ast):
    variadic_token: TokenAst
    binding: Optional[LocalVariableSingleIdentifierAst]
    _num_skipped: int = field(default=0, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variadic_token.print(printer),
            self.binding.print(printer) if self.binding else ""]
        return "".join(string)


__all__ = ["LocalVariableDestructureSkipNArgumentsAst"]
