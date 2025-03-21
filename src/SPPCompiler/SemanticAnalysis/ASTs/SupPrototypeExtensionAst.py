from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions, FunctionConflictCheckType
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


# Todo
#  - Prevent double inheritance (same type superimposed anywhere in the tree)
#  - Prevent cyclic inheritance


@dataclass
class SupPrototypeExtensionAst(Ast):
    tok_sup: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwSup))
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default_factory=lambda: Asts.GenericParameterGroupAst())
    name: Asts.TypeAst = field(default=None)
    tok_ext: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwExt))
    super_class: Asts.TypeAst = field(default=None)
    where_block: Optional[Asts.WhereBlockAst] = field(default_factory=lambda: Asts.WhereBlockAst())
    body: Asts.SupImplementationAst = field(default_factory=lambda: Asts.SupImplementationAst())

    _scope_cls: Optional[Scope] = field(init=False, default=None)

    def __post_init__(self) -> None:
        assert self.super_class

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sup.print(printer) + " ",
            self.generic_parameter_group.print(printer),
            self.name.print(printer) + " ",
            self.tok_ext.print(printer) + " ",
            self.super_class.print(printer) + " ",
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def pre_process(self, context: PreProcessingContext) -> None:
        if self.name.type_parts()[0].value[0] == "$": return
        super().pre_process(context)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Create a new scope for the superimposition.
        scope_manager.create_and_move_into_new_scope(f"<sup:{self.name} ext {self.super_class}:{self.pos}>", self)
        super().generate_top_level_scopes(scope_manager)

        # Ensure the superimposition type does not have a convention.
        if type(c := self.name.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.name, "superimposition type").scopes(scope_manager.current_scope)

        # Ensure the superimposition supertype does not have a convention.
        if type(c := self.super_class.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.super_class, "superimposition supertype").scopes(scope_manager.current_scope)

        # Generate the symbols for the generic parameter group, and the self type.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(scope_manager)
        self.body.generate_top_level_scopes(scope_manager)

        scope_manager.move_out_of_current_scope()

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.generate_top_level_aliases(scope_manager)
        scope_manager.move_out_of_current_scope()

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()

        # Cannot superimpose with a generic super class.
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())
        if cls_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(self.name, self.name, "superimposition type").scopes(scope_manager.current_scope)

        # Ensure all the generic arguments are unnamed and match the class's generic parameters.
        for generic_arg in self.name.type_parts()[0].generic_argument_group.arguments:
            if isinstance(generic_arg, Asts.GenericArgumentNamedAst.__args__):
                raise SemanticErrors.SuperimpositionGenericNamedArgumentError().add(generic_arg).scopes(scope_manager.current_scope)
            if not cls_symbol.type.generic_parameter_group.parameters.find(lambda p: p.name == generic_arg.value):
                raise SemanticErrors.SuperimpositionGenericArgumentMismatchError().add(generic_arg, self).scopes(scope_manager.current_scope)

        # Ensure the validity of the superclass, along with its generics.
        self.super_class.analyse_semantics(scope_manager)
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class.without_generics())

        if sup_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(self.super_class, self.super_class, "superimposition supertype").scopes(scope_manager.current_scope)

        # Register the superimposition as a "sup scope" and run the load steps for the body.
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class)

        # Prevent double inheritance by checking if the sup scope is already in the list.
        if existing_sup_scope := cls_symbol.scope.sup_scopes.filter(
                lambda s: isinstance(s._ast, SupPrototypeExtensionAst)).find(
                lambda s: s._ast.super_class.symbolic_eq(self.super_class, s, scope_manager.current_scope)):
            if cls_symbol.name.value[0] != "$":
                raise SemanticErrors.SuperimpositionInheritanceDuplicateSuperclassError(existing_sup_scope._ast.super_class, self.super_class).scopes(scope_manager.current_scope)

        # Prevent cyclic inheritance by checking if the scopes are already registered the other way around.
        if existing_sup_scope := sup_symbol.scope.sup_scopes.filter(
                lambda s: isinstance(s._ast, SupPrototypeExtensionAst)).find(
                lambda s: s._ast.super_class.symbolic_eq(self.name, s, scope_manager.current_scope)):
            raise SemanticErrors.SuperimpositionInheritanceCyclicInheritanceError(existing_sup_scope._ast.super_class, self.name).scopes(scope_manager.current_scope)

        # Register sup and sub scopes.
        cls_symbol.scope._direct_sup_scopes.append(scope_manager.current_scope)
        cls_symbol.scope._direct_sup_scopes.append(sup_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(cls_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(scope_manager.current_scope)

        # Mark the class as copyable if the Copy type is the super class.
        if self.super_class.symbolic_eq(CommonTypes.Copy(), scope_manager.current_scope):
            cls_symbol.is_copyable = True

        # Run the inject steps for the body.
        self._scope_cls = cls_symbol.scope
        self.body.load_super_scopes(scope_manager)

        # Prevent duplicate attributes by checking if the attributes appear in any super class.
        super_class_attribute_names = sup_symbol.scope.sup_scopes.filter(
            lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)).map(lambda s: s._ast.body.members).flat().map_attr("name")
        existing_attribute_names = (cls_symbol.scope.sup_scopes + Seq([cls_symbol.scope])).filter(
            lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)).map(lambda s: s._ast.body.members).flat().map_attr("name")
        if duplicates := (existing_attribute_names + super_class_attribute_names).non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "attribute").scopes(scope_manager.current_scope)

        # Mark the type as abstract if the superclass is abstract.
        if sup_symbol.is_abstract:
            cls_symbol.is_abstract = True

        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Move to the next scope.
        scope_manager.move_to_next_scope()

        # Get the class and super class symbols.
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class)

        # Analyse the generic parameter group.
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)

        # Check every generic parameter is constrained by the type.
        if unconstrained := self.generic_parameter_group.parameters.filter(lambda p: not self.name.contains_generic(p.name)):
            if self.name.type_parts()[0].value[0] != "$":
                raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(unconstrained[0], self.name).scopes(scope_manager.current_scope)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_opt():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(optional[0]).scopes(scope_manager.current_scope)

        # Analyse the name, where block, and body.
        self.name.analyse_semantics(scope_manager, **kwargs)
        self.super_class.analyse_semantics(scope_manager, **kwargs)
        self.where_block.analyse_semantics(scope_manager, **kwargs)
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Check every member on the superimposition exists on the super class.
        for member in self.body.members.filter_to_type(SupPrototypeExtensionAst):
            this_method = member.body.members[-1]
            base_method = AstFunctions.check_for_conflicting_method(
                scope_manager.current_scope, sup_symbol.scope, this_method, FunctionConflictCheckType.InvalidOverride)

            # Check the base method exists.
            if not base_method:
                raise SemanticErrors.SuperimpositionInheritanceMethodInvalidError().add(this_method.name, self.super_class).scopes(scope_manager.current_scope)

            # Check the base method is virtual or abstract.
            if not (base_method._virtual or base_method._abstract):
                raise SemanticErrors.SuperimpositionInheritanceNonVirtualMethodOverriddenError().add(base_method.name, self.super_class).scopes(scope_manager.current_scope)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SupPrototypeExtensionAst"]
