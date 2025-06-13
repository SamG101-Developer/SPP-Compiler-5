from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


# Todo: check the ast_initialization (when there's aliases) - what do we want to show exactly?


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
    def extract_names(self) -> List[Asts.IdentifierAst]:
        return [self.name]

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    def analyse_semantics(self, sm: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:
        inferred_type = value.infer_type(sm, **kwargs)

        # Create a variable symbol for this identifier and value.
        sym = VariableSymbol(
            name=self.alias.name if self.alias else self.name,
            type=kwargs.pop("explicit_type", inferred_type) or inferred_type,
            is_mutable=self.tok_mut is not None,
            visibility=Visibility.Public)

        # Set the initialization ast (for errors). Increment the initialization counter for initialized variables.
        sym.memory_info.ast_initialization = self.name
        sym.memory_info.ast_initialization_old = self.name

        if not kwargs.get("from_non_init", False):
            sym.memory_info.initialization_counter = 1

            # Set any borrow asts based on the potentially symbolic value being set to this variable.
            if convention := inferred_type.convention:
                sym.memory_info.ast_borrowed = value
                sym.memory_info.is_borrow_mut = convention if isinstance(convention, Asts.ConventionMutAst) else False
                sym.memory_info.is_borrow_ref = convention if isinstance(convention, Asts.ConventionRefAst) else False
        else:
            sym.memory_info.ast_moved = self

        sm.current_scope.add_symbol(sym)

    def check_memory(self, sm: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:
        sym = sm.current_scope.get_symbol(self.alias.name if self.alias else self.name)
        if not kwargs.get("from_non_init", False):
            value.check_memory(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(
                value, self, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
                check_pins=True, mark_moves=True, **kwargs)
            sym.memory_info.initialized_by(self.name)


__all__ = [
    "LocalVariableSingleIdentifierAst"]
