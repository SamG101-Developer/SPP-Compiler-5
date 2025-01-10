from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereConstraintsAst import WhereConstraintsAst


@dataclass
class WhereConstraintsGroupAst(Ast, Default):
    tok_left_brack: TokenAst
    constraints: Seq[WhereConstraintsAst]
    tok_right_brack: TokenAst

    def __post_init__(self) -> None:
        # Convert the constraints into a sequence.
        self.constraints = Seq(self.constraints)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_brack.print(printer),
            self.constraints.print(printer, ", "),
            self.tok_right_brack.print(printer)]
        return "".join(string)

    @staticmethod
    def default() -> WhereConstraintsGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return WhereConstraintsGroupAst(-1, TokenAst.default(SppTokenType.TkBrackL), Seq(), TokenAst.default(SppTokenType.TkBrackR))


__all__ = ["WhereConstraintsGroupAst"]
