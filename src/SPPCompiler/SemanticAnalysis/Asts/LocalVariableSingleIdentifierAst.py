from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class LocalVariableSingleIdentifierAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    alias: Optional[Asts.LocalVariableSingleIdentifierAliasAst] = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.name.print(printer),
            (" " + self.alias.print(printer)) if self.alias is not None else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.alias.pos_end if self.alias else self.name.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return Seq([self.name])

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    def analyse_semantics(self, sm: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:
        inferred_type = value.infer_type(sm, **kwargs)

        # Create a variable symbol for this identifier and value.
        symbol = VariableSymbol(
            name=self.alias.name if self.alias else self.name,
            type=kwargs.pop("explicit_type", inferred_type) or inferred_type,
            is_mutable=self.tok_mut is not None,
            visibility=Visibility.Public)

        # Set the initialization ast (for errors). Increment the initialization counter for initialized variables.
        symbol.memory_info.ast_initialization = self.name
        if not isinstance(value, Asts.TypeAst):
            symbol.memory_info.initialization_counter = 1
            AstMemoryUtils.enforce_memory_integrity(value, self, sm)
        else:
            symbol.memory_info.ast_moved = self

        sm.current_scope.add_symbol(symbol)


__all__ = [
    "LocalVariableSingleIdentifierAst"]
