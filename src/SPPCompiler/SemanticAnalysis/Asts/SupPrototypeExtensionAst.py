from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from typing import TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


# Todo
#  - Add tests for double inheritance
#  - Add tests for cyclic inheritance
#  - Only allow 1 Gen[T] superimposition
#  - Error if the type doesn't exist


@dataclass(slots=True)
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
        Asts.Ast.pre_process(self, ctx)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a new scope for the superimposition.
        sm.create_and_move_into_new_scope(f"<sup:{self.name} ext {self.super_class}:{self.pos}>", self)
        Asts.Ast.generate_top_level_scopes(self, sm)

        # Ensure the superimposition type does not have a convention.
        if c := self.name.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.name, "superimposition type").scopes(sm.current_scope)

        # Ensure the superimposition supertype does not have a convention.
        if c := self.super_class.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.super_class, "superimposition supertype").scopes(sm.current_scope)

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

        # Check every generic parameter is constrained by the type.
        if unconstrained := [p for p in self.generic_parameter_group.parameters if not self.name.contains_generic(p.name)]:
            if self.name.type_parts()[0].value[0] != "$":
                raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(
                    unconstrained[0], self.name).scopes(sm.current_scope)

        self.body.qualify_types(sm, **kwargs)
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        # Cannot superimpose with a generic super class.
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

            if not [p for p in other_cls_symbol.type.generic_parameter_group.parameters if p.name == generic_arg.value]:
                raise SemanticErrors.SuperimpositionGenericArgumentMismatchError().add(
                    generic_arg, self.tok_sup).scopes(sm.current_scope)

        self.super_class.analyse_semantics(sm, **kwargs)
        self.super_class = sm.current_scope.get_symbol(self.super_class).fq_name

        sup_symbol = sm.current_scope.get_symbol(self.super_class.without_generics())
        if sup_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(
                self.super_class, self.super_class, "superimposition supertype").scopes(sm.current_scope)

        # Prevent double inheritance by checking if the sup scope is already in the list.
        if existing_sup_scope := [s for s in sup_symbol.scope.sup_scopes if isinstance(s._ast, SupPrototypeExtensionAst) and s._ast.super_class.symbolic_eq(self.name, s, sm.current_scope)]:
            raise SemanticErrors.SuperimpositionExtensionCyclicExtensionError().add(
                existing_sup_scope[0]._ast.super_class, self.name).scopes(sm.current_scope)

        # Prevent cyclic inheritance by checking if the scopes are already registered the other way around.
        if cls_symbol.name.value[0] != "$":
            if existing_sup_scope := [s for s in cls_symbol.scope.sup_scopes if isinstance(s._ast, SupPrototypeExtensionAst) and s._ast.super_class.symbolic_eq(self.super_class, s, sm.current_scope)]:
                raise SemanticErrors.SuperimpositionExtensionDuplicateSuperclassError().add(
                    existing_sup_scope[0]._ast.super_class, self.super_class).scopes(sm.current_scope)

        sup_symbol = sup_symbol.scope.get_symbol(self.super_class)

        # Mark the class as copyable if the Copy type is the super class.
        if self.super_class.symbolic_eq(CommonTypesPrecompiled.COPY, sm.current_scope):
            cls_symbol.is_copyable = True

        # Run the inject steps for the body.
        self._scope_cls = cls_symbol.scope
        self.body.load_super_scopes(sm, **kwargs)

        # Prevent duplicate attributes by checking if the attributes appear in any super class.
        # Todo: move beneath symbol logic and follow "use"/"cmp" checks?
        super_class_attribute_names: Seq[Asts.TypeAst] = SequenceUtils.flatten([
            [m.name for m in s._ast.body.members]
            for s in sup_symbol.scope.sup_scopes + [sup_symbol.scope]
            if isinstance(s._ast, Asts.ClassPrototypeAst)])

        existing_attribute_names: Seq[Asts.TypeAst] = SequenceUtils.flatten([
            [m.name for m in s._ast.body.members]
            for s in cls_symbol.scope.sup_scopes + [cls_symbol.scope]
            if isinstance(s._ast, Asts.ClassPrototypeAst)])

        if duplicates := SequenceUtils.duplicates(existing_attribute_names + super_class_attribute_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[1], "attribute").scopes(sm.current_scope)

        # Register sup and sub scopes.
        cls_symbol.scope._direct_sup_scopes.append(sup_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(cls_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(sm.current_scope)

        # Prevent duplicate types by checking if the types appear in any super class (allow overrides though).
        existing_type_names = SequenceUtils.flatten([
            [m.new_type for m in s._ast.body.members if isinstance(m, Asts.SupUseStatementAst)]
            for s in cls_symbol.scope.sup_scopes
            if isinstance(s._ast, Asts.SupPrototypeAst)
        ])

        if duplicates := SequenceUtils.duplicates(existing_type_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[1], "associated type").scopes(sm.current_scope)

        # Prevent duplicate cmp declarations by checking if the cmp statements appear in any super class. Use the "$"
        # check to skip checking functions, which can be overridden.
        existing_cmp_names = SequenceUtils.flatten([
            [m.name for m in s._ast.body.members if isinstance(m, Asts.SupCmpStatementAst) and m.type.type_parts()[-1].value[0] != "$"]  # todo: has the type been analysed at this point
            for s in cls_symbol.scope.sup_scopes
            if isinstance(s._ast, Asts.SupPrototypeAst)
        ])

        if duplicates := SequenceUtils.duplicates(existing_cmp_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[1], "associated const").scopes(sm.current_scope)

        cls_symbol.scope._direct_sup_scopes.append(sm.current_scope)
        sm.move_out_of_current_scope()

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Move to the next scope.
        sm.move_to_next_scope()
        sup_symbol = sm.current_scope.get_symbol(self.super_class)

        # Add the "Self" symbol into the scope.
        if self.name.type_parts()[0].value[0] != "$":
            cls_symbol = sm.current_scope.get_symbol(self.name.without_generics())
            self_symbol = TypeSymbol(
                name=Asts.GenericIdentifierAst.from_type(CommonTypes.Self(self.name.pos)), type=cls_symbol.type,
                scope=cls_symbol.scope)
            sm.current_scope.add_symbol(self_symbol)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_optional_params():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(
                optional[0]).scopes(sm.current_scope)

        # Check every member on the superimposition exists on the super class (all sup scopes must be loaded here).
        for member in self.body.members:
            match member:
                case SupPrototypeExtensionAst():
                    # Get the method and identify the base method it is overriding.
                    this_method = member.body.members[-1]
                    base_method = AstFunctionUtils.check_for_conflicting_override(
                        sm.current_scope, sup_symbol.scope, this_method)

                    # Check the base method exists.
                    if not base_method:
                        raise SemanticErrors.SuperimpositionExtensionMethodInvalidError().add(
                            this_method.name, self.super_class).scopes(sm.current_scope)

                    # Check the base method is virtual or abstract.
                    if not (base_method._virtual or base_method._abstract):
                        raise SemanticErrors.SuperimpositionExtensionNonVirtualMethodOverriddenError().add(
                            base_method.name, self.super_class).scopes(sm.current_scope)

                case Asts.SupUseStatementAst():
                    # Get the associated type from the superclass directly.
                    this_type = member.new_type
                    base_type = sup_symbol.scope.get_symbol(this_type, exclusive=True)

                    # Check to see if the base type exists.
                    if not base_type:
                        raise SemanticErrors.SuperimpositionExtensionUseStatementInvalidError().add(
                            member, self.super_class).scopes(sm.current_scope)

                case Asts.CmpStatementAst():
                    # Get the associated constant from the superclass directly.
                    this_const = member.name
                    base_const = sup_symbol.scope.get_symbol(this_const, exclusive=True)

                    # Check to see if the base type exists.
                    if not base_const:
                        raise SemanticErrors.SuperimpositionExtensionCmpStatementInvalidError().add(
                            member, self.super_class).scopes(sm.current_scope)

        # Pre-analyse all the members.
        self.body.pre_analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Move to the next scope.
        sm.move_to_next_scope()

        # Analyse the generic parameter group, name, where block, and body.
        self.name.analyse_semantics(sm, **kwargs)
        self.super_class.analyse_semantics(sm, **kwargs)
        self.where_block.analyse_semantics(sm, **kwargs)
        self.body.analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()


__all__ = [
    "SupPrototypeExtensionAst"]
