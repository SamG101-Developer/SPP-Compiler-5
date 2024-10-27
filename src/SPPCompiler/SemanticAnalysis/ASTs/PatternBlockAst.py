from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.PatternGuardAst import PatternGuardAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantAst import PatternVariantAst
    from SPPCompiler.SemanticAnalysis.ASTs.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst


@dataclass
class PatternBlockAst(Ast, Stage4_SemanticAnalyser):
    comp_operator: Optional[TokenAst]
    patterns: Seq[PatternVariantAst]
    guard: Optional[PatternGuardAst]
    body: Optional[InnerScopeAst[StatementAst]]

    def __post_init__(self) -> None:
        # Convert the patterns into a sequence.
        self.patterns = Seq(self.patterns)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.comp_operator.print(printer) if self.comp_operator else "",
            self.patterns.print(printer, ", "),
            self.guard.print(printer) if self.guard else "",
            self.body.print(printer) if self.body else ""]
        return "".join(string)

    def analyse_semantics(self, scope_handler: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["PatternBlockAst"]
