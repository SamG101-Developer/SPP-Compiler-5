from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import functools, std

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LocalVariableSingleIdentifierAst(Ast, VariableNameExtraction, CompilerStages):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    alias: Optional[Asts.LocalVariableSingleIdentifierAliasAst] = field(default=None)

    def __post_init__(self) -> None:
        assert self.name

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.name.print(printer),
            (" " + self.alias.print(printer)) if self.alias is not None else ""]
        return "".join(string)

    @functools.cached_property
    @std.override_method
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return Seq([self.name])

    @functools.cached_property
    @std.override_method
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:

        # Create a variable symbol for this identifier and value.
        value_type = value.infer_type(scope_manager, **kwargs).type
        symbol = VariableSymbol(
            name=self.alias.name if self.alias else self.name,
            type=value_type,
            is_mutable=self.tok_mut is not None,
            visibility=AstVisibility.Public)

        # Set the initialization ast (for errors). Increment the initialization counter for initialized variables.
        symbol.memory_info.ast_initialization = self.name
        if not isinstance(value, Asts.TypeAst):
            symbol.memory_info.initialization_counter = 1
            AstMemoryHandler.enforce_memory_integrity(value, self, scope_manager)
        else:
            symbol.memory_info.ast_moved = self

        scope_manager.current_scope.add_symbol(symbol)


__all__ = ["LocalVariableSingleIdentifierAst"]
