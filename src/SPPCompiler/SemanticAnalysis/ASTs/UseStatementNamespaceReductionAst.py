from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementNamespaceReductionBodyAst import UseStatementNamespaceReductionBodyAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UseStatementNamespaceReductionAst(Ast, Stage2_SymbolGenerator, Stage4_SemanticAnalyser):
    body: UseStatementNamespaceReductionBodyAst

    _generated: bool = field(default=False, init=False, repr=False)
    _new_asts: Seq[Ast] = field(default_factory=Seq, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.body.print(printer)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["UseStatementNamespaceReductionAst"]
