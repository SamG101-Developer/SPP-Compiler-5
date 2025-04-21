from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class SupPrototypeFunctionsAst(Asts.Ast):
    tok_sup: Asts.TokenAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    where_block: Optional[Asts.WhereBlockAst] = field(default=None)
    body: Asts.SupImplementationAst = field(default=None)

    _scope_cls: Optional[Scope] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.tok_sup = self.tok_sup or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwSup)
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst(pos=self.pos)
        self.where_block = self.where_block or Asts.WhereBlockAst(pos=self.pos)
        self.body = self.body or Asts.SupImplementationAst(pos=self.pos)
        assert self.name is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sup.print(printer) + " ",
            self.generic_parameter_group.print(printer),
            self.name.print(printer) + " ",
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the members of this superimposition.
        super().pre_process(ctx)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a new scope for the superimposition.
        sm.create_and_move_into_new_scope(f"<sup:{self.name}:{self.pos}>", self)
        super().generate_top_level_scopes(sm)

        # Ensure the superimposition type does not have a convention.
        if c := self.name.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.name, "superimposition type").scopes(sm.current_scope)

        # Generate the symbols for the generic parameter group, and the self type.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(sm)
        self.body.generate_top_level_scopes(sm)

        sm.move_out_of_current_scope()

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        self.body.generate_top_level_aliases(sm)
        sm.move_out_of_current_scope()

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.body.qualify_types(sm, **kwargs)
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        # Cannot superimpose over a generic type.
        cls_symbol = sm.current_scope.get_symbol(self.name.without_generics())
        if cls_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(
                self.name, self.name, "superimposition type").scopes(sm.current_scope)

        # Ensure all the generic arguments are unnamed and match the class's generic parameters.
        other_cls_symbol = sm.current_scope.get_symbol(self.name.without_generics(), ignore_alias=True)
        for generic_arg in self.name.type_parts()[0].generic_argument_group.arguments:
            if isinstance(generic_arg, Asts.GenericArgumentNamedAst.__args__):
                raise SemanticErrors.SuperimpositionGenericNamedArgumentError().add(
                    generic_arg).scopes(sm.current_scope)

            if not other_cls_symbol.type.generic_parameter_group.parameters.find(lambda p: p.name == generic_arg.value):
                raise SemanticErrors.SuperimpositionGenericArgumentMismatchError().add(
                    generic_arg, self.tok_sup).scopes(sm.current_scope)

        # Register the superimposition as a "sup scope" and run the load steps for the body.
        cls_symbol.scope._direct_sup_scopes.append(sm.current_scope)
        self._scope_cls = cls_symbol.scope
        self.body.load_super_scopes(sm)

        sm.move_out_of_current_scope()

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        # Add the "Self" symbol into the scope.
        if self.name.type_parts()[0].value[0] != "$":
            cls_symbol = sm.current_scope.get_symbol(self.name.without_generics())
            self_symbol = TypeSymbol(
                name=Asts.GenericIdentifierAst.from_type(CommonTypes.Self(self.name.pos)), type=cls_symbol.type,
                scope=cls_symbol.scope)
            sm.current_scope.add_symbol(self_symbol)
            # print(f"Added {self_symbol} to scope '{sm.current_scope.name}'.")

        # Check every generic parameter is constrained by the type.
        if unconstrained := self.generic_parameter_group.parameters.filter(lambda p: not self.name.contains_generic(p.name)):
            raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(
                unconstrained[0], self.name).scopes(sm.current_scope)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_optional_params():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(
                optional[0]).scopes(sm.current_scope)

        # Pre-analyse all the members.
        self.body.pre_analyse_semantics(sm, **kwargs)

        sm.move_out_of_current_scope()

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:

        # Move to the next scope.
        sm.move_to_next_scope()

        # Analyse the generic parameter group, name, where block, and body.
        self.name.analyse_semantics(sm, **kwargs)
        self.where_block.analyse_semantics(sm, **kwargs)
        self.body.analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()


__all__ = [
    "SupPrototypeFunctionsAst"]
