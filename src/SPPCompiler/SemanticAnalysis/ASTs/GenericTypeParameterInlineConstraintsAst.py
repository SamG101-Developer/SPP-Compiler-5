from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericTypeParameterInlineConstraintsAst(Ast, Default, CompilerStages):
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
        from SPPCompiler.SemanticAnalysis import TokenAst
        return GenericTypeParameterInlineConstraintsAst(-1, TokenAst.default(TokenType.TkColon), Seq())

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        for c in self.constraints:
            c.analyse_semantics(scope_manager, **kwargs)

        # Check there are duplicate constraints types.
        for i, t in self.constraints.enumerate():
            for j, u in self.constraints[i + 1:].enumerate():
                if t.symbolic_eq(u, scope_manager.current_scope):
                    raise SemanticErrors.IdentifierDuplicationError(t, u)


__all__ = ["GenericTypeParameterInlineConstraintsAst"]
