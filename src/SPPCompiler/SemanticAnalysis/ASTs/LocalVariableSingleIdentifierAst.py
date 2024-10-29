from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.AstVisibility import AstVisibility
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class LocalVariableSingleIdentifierAst(Ast, Stage4_SemanticAnalyser):
    tok_mut: Optional[TokenAst]
    name: IdentifierAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.name.print(printer)]
        return "".join(string)

    def analyse_semantics(self, scope_manager: ScopeManager, value: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol, MemoryInfo

        # Create a variable symbol for this identifier and value.
        value_type = value.infer_type(scope_manager, **kwargs).type
        symbol = VariableSymbol(
            name=self.name,
            type=value_type,
            is_mutable=self.tok_mut is not None,
            memory_info=MemoryInfo(ast_initialization=self.name),
            visibility=AstVisibility.Public)
        scope_manager.current_scope.add_symbol(symbol)


__all__ = ["LocalVariableSingleIdentifierAst"]
