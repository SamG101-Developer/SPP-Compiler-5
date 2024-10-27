from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereConstraintsGroupAst import WhereConstraintsGroupAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class WhereBlockAst(Ast, Default, Stage4_SemanticAnalyser):
    tok_where: TokenAst
    constraint_group: WhereConstraintsGroupAst

    @staticmethod
    def default() -> WhereBlockAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import WhereConstraintsGroupAst, TokenAst
        return WhereBlockAst(-1, TokenAst.default(TokenType.KwWhere), WhereConstraintsGroupAst.default())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.constraint_group.constraints:
            string = [
                self.tok_where.print(printer) + " ",
                self.constraint_group.print(printer)]
        else:
            string = []
        return "".join(string)

    def analyse_semantics(self, scope_handler: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["WhereBlockAst"]
