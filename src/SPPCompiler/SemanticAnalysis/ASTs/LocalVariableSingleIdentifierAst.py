from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class LocalVariableSingleIdentifierAst(Ast, VariableNameExtraction, CompilerStages):
    tok_mut: Optional[TokenAst]
    name: IdentifierAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.name.print(printer)]
        return "".join(string)

    @functools.cached_property
    def extract_names(self) -> Seq[IdentifierAst]:
        return Seq([self.name])

    @functools.cached_property
    def extract_name(self) -> IdentifierAst:
        return self.name

    def analyse_semantics(self, scope_manager: ScopeManager, value: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
        from SPPCompiler.SemanticAnalysis import TypeAst

        # Create a variable symbol for this identifier and value.
        value_type = value.infer_type(scope_manager, **kwargs).type
        symbol = VariableSymbol(
            name=self.name,
            type=value_type,
            is_mutable=self.tok_mut is not None,
            visibility=AstVisibility.Public)

        # Set the initialization ast (for errors). Increment the initialization counter for initialized variables.
        symbol.memory_info.ast_initialization = self.name
        if not isinstance(value, TypeAst):
            symbol.memory_info.initialization_counter = 1
        else:
            symbol.memory_info.ast_moved = self

        scope_manager.current_scope.add_symbol(symbol)


__all__ = ["LocalVariableSingleIdentifierAst"]
