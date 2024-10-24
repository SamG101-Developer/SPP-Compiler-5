from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class GenericTypeParameterInlineConstraintsAst(Ast, Default):
    tok_colon: TokenAst
    constraints: Seq[TypeAst]

    def __post_init__(self) -> None:
        # Convert the constraints into a sequence.
        self.constraints = Seq(self.constraints)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.constraints:
            string = [
                self.tok_colon.print(printer),
                self.constraints.print(printer, ", ")]
        else:
            string = []
        return "".join(string)

    @staticmethod
    def default() -> GenericTypeParameterInlineConstraintsAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return GenericTypeParameterInlineConstraintsAst(-1, TokenAst.default(TokenType.TkColon), Seq())


__all__ = ["GenericTypeParameterInlineConstraintsAst"]
