from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from typing import TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils, FunctionConflictCheckType
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


# Todo
#  - Prevent double inheritance (same type superimposed anywhere in the tree)
#  - Prevent cyclic inheritance
#  - Only allow 1 Gen[T] superimposition


@dataclass
class SupPrototypeExtensionAst(Asts.Ast):
    tok_sup: Asts.TokenAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    tok_ext: Asts.TokenAst = field(default=None)
    super_class: Asts.TypeAst = field(default=None)
    where_block: Optional[Asts.WhereBlockAst] = field(default=None)
    body: Asts.SupImplementationAst = field(default=None)

    _scope_cls: Optional[Scope] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.tok_sup = self.tok_sup or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwSup)
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst(pos=self.pos)
        self.tok_ext = self.tok_ext or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwExt)
        self.where_block = self.where_block or Asts.WhereBlockAst(pos=self.pos)
        self.body = self.body or Asts.SupImplementationAst(pos=self.pos)
        assert self.name is not None and self.super_class is not None

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

    def pre_process(self, ctx: PreProcessingContext) -> None:
        if self.name.type_parts()[0].value[0] == "$": return
        super().pre_process(ctx)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a new scope for the superimposition.
        sm.create_and_move_into_new_scope(f"<sup:{self.name} ext {self.super_class}:{self.pos}>", self)
        super().generate_top_level_scopes(sm)

        # Ensure the superimposition type does not have a convention.
        if (cs := self.name.get_conventions()).not_empty():
            raise SemanticErrors.InvalidConventionLocationError().add(
                cs[0], self.name, "superimposition type").scopes(sm.current_scope)

        # Ensure the superimposition supertype does not have a convention.
        if (cs := self.super_class.get_conventions()).not_empty():
            raise SemanticErrors.InvalidConventionLocationError().add(
                cs[0], self.super_class, "superimposition supertype").scopes(sm.current_scope)

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

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        # Cannot superimpose with a generic super class.
        cls_symbol = sm.current_scope.get_symbol(self.name.without_generics())
        if cls_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(
                self.name, self.name, "superimposition type").scopes(sm.current_scope)

        # Ensure all the generic arguments are unnamed and match the class's generic parameters.
        for generic_arg in self.name.type_parts()[0].generic_argument_group.arguments:
            if isinstance(generic_arg, Asts.GenericArgumentNamedAst.__args__):
                raise SemanticErrors.SuperimpositionGenericNamedArgumentError().add(
                    generic_arg).scopes(sm.current_scope)

            if not cls_symbol.type.generic_parameter_group.parameters.find(lambda p: p.name == generic_arg.value):
                raise SemanticErrors.SuperimpositionGenericArgumentMismatchError().add(
                    generic_arg, self).scopes(sm.current_scope)

        # Ensure the validity of the superclass, along with its generics.
        self.super_class.analyse_semantics(sm)
        self.super_class = sm.current_scope.get_symbol(self.super_class).fq_name

        sup_symbol = sm.current_scope.get_symbol(self.super_class.without_generics())

        if sup_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(
                self.super_class, self.super_class, "superimposition supertype").scopes(sm.current_scope)

        # Register the superimposition as a "sup scope" and run the load steps for the body.
        sup_symbol = sm.current_scope.get_symbol(self.super_class)

        # Prevent double inheritance by checking if the sup scope is already in the list.
        if existing_sup_scope := cls_symbol.scope.sup_scopes.filter(
                lambda s: isinstance(s._ast, SupPrototypeExtensionAst)).find(
                lambda s: s._ast.super_class.symbolic_eq(self.super_class, s, sm.current_scope)):
            if cls_symbol.name.value[0] != "$":
                raise SemanticErrors.SuperimpositionInheritanceDuplicateSuperclassError().add(
                    existing_sup_scope._ast.super_class, self.super_class).scopes(sm.current_scope)

        # Prevent cyclic inheritance by checking if the scopes are already registered the other way around.
        if existing_sup_scope := sup_symbol.scope.sup_scopes.filter(
                lambda s: isinstance(s._ast, SupPrototypeExtensionAst)).find(
                lambda s: s._ast.super_class.symbolic_eq(self.name, s, sm.current_scope)):
            raise SemanticErrors.SuperimpositionInheritanceCyclicInheritanceError().add(
                existing_sup_scope._ast.super_class, self.name).scopes(sm.current_scope)

        # Register sup and sub scopes.
        cls_symbol.scope._direct_sup_scopes.append(sm.current_scope)
        cls_symbol.scope._direct_sup_scopes.append(sup_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(cls_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(sm.current_scope)

        # Mark the class as copyable if the Copy type is the super class.
        if self.super_class.symbolic_eq(CommonTypes.Copy(0), sm.current_scope):
            cls_symbol.is_copyable = True

        # Run the inject steps for the body.
        self._scope_cls = cls_symbol.scope
        self.body.load_super_scopes(sm)

        # Prevent duplicate attributes by checking if the attributes appear in any super class.
        super_class_attribute_names = sup_symbol.scope.sup_scopes.filter(
            lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)).map(
            lambda s: s._ast.body.members).flat().map_attr("name")

        existing_attribute_names = (cls_symbol.scope.sup_scopes + Seq([cls_symbol.scope])).filter(
            lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)).map(
            lambda s: s._ast.body.members).flat().map_attr("name")

        if duplicates := (existing_attribute_names + super_class_attribute_names).non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0][0], duplicates[0][1], "attribute").scopes(sm.current_scope)

        sm.move_out_of_current_scope()

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Move to the next scope.
        sm.move_to_next_scope()

        # Get the class and super class symbols.
        cls_symbol = sm.current_scope.get_symbol(self.name.without_generics())
        sup_symbol = sm.current_scope.get_symbol(self.super_class)

        # Analyse the generic parameter group.
        self.generic_parameter_group.analyse_semantics(sm, **kwargs)

        # Check every generic parameter is constrained by the type.
        if unconstrained := self.generic_parameter_group.parameters.filter(lambda p: not self.name.contains_generic(p.name)):
            if self.name.type_parts()[0].value[0] != "$":
                raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(
                    unconstrained[0], self.name).scopes(sm.current_scope)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_optional_params():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(
                optional[0]).scopes(sm.current_scope)

        # Analyse the name, where block, and body.
        self.name.analyse_semantics(sm, **kwargs)
        self.super_class.analyse_semantics(sm, **kwargs)
        self.where_block.analyse_semantics(sm, **kwargs)
        self.body.analyse_semantics(sm, **kwargs)

        # Check every member on the superimposition exists on the super class.
        for member in self.body.members.filter_to_type(SupPrototypeExtensionAst):
            this_method = member.body.members[-1]
            base_method = AstFunctionUtils.check_for_conflicting_method(
                sm.current_scope, sup_symbol.scope, this_method, FunctionConflictCheckType.InvalidOverride)

            # Check the base method exists.
            if not base_method:
                raise SemanticErrors.SuperimpositionInheritanceMethodInvalidError().add(
                    this_method.name, self.super_class).scopes(sm.current_scope)

            # Check the base method is virtual or abstract.
            if not (base_method._virtual or base_method._abstract):
                raise SemanticErrors.SuperimpositionInheritanceNonVirtualMethodOverriddenError().add(
                    base_method.name, self.super_class).scopes(sm.current_scope)

        # Move out of the current scope.
        sm.move_out_of_current_scope()


__all__ = [
    "SupPrototypeExtensionAst"]
