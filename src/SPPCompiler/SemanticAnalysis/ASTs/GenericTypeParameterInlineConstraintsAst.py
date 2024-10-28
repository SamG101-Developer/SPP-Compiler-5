from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericTypeParameterInlineConstraintsAst(Ast, Default, Stage4_SemanticAnalyser):
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

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.constraints.for_each(lambda constraint: constraint.analyse_semantics(scope_manager, **kwargs))


__all__ = ["GenericTypeParameterInlineConstraintsAst"]
