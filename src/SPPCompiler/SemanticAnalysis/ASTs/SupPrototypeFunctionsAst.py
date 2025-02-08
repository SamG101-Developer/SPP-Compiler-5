from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class SupPrototypeFunctionsAst(Ast):
    tok_sup: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwSup))
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default_factory=lambda: Asts.GenericParameterGroupAst())
    name: Asts.TypeAst = field(default=None)
    where_block: Optional[Asts.WhereBlockAst] = field(default_factory=lambda: Asts.WhereBlockAst())
    body: Asts.SupImplementationAst = field(default_factory=lambda: Asts.SupImplementationAst())

    _scope_cls: Optional[Scope] = field(init=False, default=None)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sup.print(printer) + " ",
            self.generic_parameter_group.print(printer),
            self.name.print(printer) + " ",
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @std.override_method
    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the members of this superimposition.
        super().pre_process(context)
        self.body.pre_process(self)

    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Create a new scope for the superimposition.
        scope_manager.create_and_move_into_new_scope(f"<sup:{self.name}:{self.pos}>", self)
        super().generate_top_level_scopes(scope_manager)

        # Generate the symbols for the generic parameter group, and the self type.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(scope_manager)
        self.body.generate_top_level_scopes(scope_manager)

        scope_manager.move_out_of_current_scope()

    @std.override_method
    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.generate_top_level_aliases(scope_manager)
        scope_manager.move_out_of_current_scope()

    @std.override_method
    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()

        # Cannot superimpose over a generic type.
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())
        if cls_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(self.name, self.name, "superimposition type")

        # Register the superimposition as a "sup scope" and run the load steps for the body.
        cls_symbol.scope._direct_sup_scopes.append(scope_manager.current_scope)
        self._scope_cls = cls_symbol.scope
        self.body.load_super_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    @std.override_method
    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())

        # Mark the type as abstract if any of the functions are abstract.
        if self.body.members.filter_to_type(Asts.SupPrototypeExtensionAst).map(lambda s: s.body.members[-1]).filter(lambda m: m._abstract):
            cls_symbol.is_abstract = True

        self.body.postprocess_super_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    @std.override_method
    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        self.body.regenerate_generic_aliases(scope_manager)
        scope_manager.move_out_of_current_scope()

    @std.override_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        self.body.regenerate_generic_types(scope_manager)
        scope_manager.move_out_of_current_scope()

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:

        # Move to the next scope.
        scope_manager.move_to_next_scope()

        # Analyse the generic parameter group.
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)

        # Check every generic parameter is constrained by the type.
        if unconstrained := self.generic_parameter_group.parameters.filter(lambda p: not self.name.contains_generic(p.name)):
            raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(unconstrained[0], self.name)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_opt():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(optional[0])

        # Analyse the name, where block, and body.
        # self.name.analyse_semantics(scope_manager, **kwargs)
        self.where_block.analyse_semantics(scope_manager, **kwargs)
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SupPrototypeFunctionsAst"]
