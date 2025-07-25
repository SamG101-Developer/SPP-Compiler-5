from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


# Todo
#  - Only allow 1 Gen superimposition?
#  - Only allow 1 Try superimposition?


@dataclass(slots=True, repr=False)
class SupPrototypeExtensionAst(Asts.Ast):
    tok_sup: Asts.TokenAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    tok_ext: Asts.TokenAst = field(default=None)
    super_class: Asts.TypeAst = field(default=None)
    where_block: Optional[Asts.WhereBlockAst] = field(default=None)
    body: Asts.SupImplementationAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_sup = self.tok_sup or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwSup)
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst(pos=self.pos)
        self.tok_ext = self.tok_ext or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwExt)
        self.where_block = self.where_block or Asts.WhereBlockAst(pos=self.pos)
        self.body = self.body or Asts.SupImplementationAst(pos=self.pos)

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
        return self.super_class.pos_end

    def _check_cyclic_extension(self, sup_symbol: TypeSymbol, check_scope: Scope) -> None:
        # Prevent double inheritance by checking if the scopes are already registered the other way around.
        existing_sup_scope = [
            s for s in sup_symbol.scope.sup_scopes
            if (type(s._ast) is SupPrototypeExtensionAst)
                and AstTypeUtils.relaxed_symbolic_eq(self.super_class, s._ast.name, check_scope, s)
                and AstTypeUtils.symbolic_eq(s._ast.super_class, self.name, s, check_scope)]

        if existing_sup_scope:
            raise SemanticErrors.SuperimpositionExtensionCyclicExtensionError().add(
                existing_sup_scope[0]._ast.super_class, self.name).scopes(check_scope)

    def _check_double_extension(self, cls_symbol: TypeSymbol, sup_symbol: TypeSymbol, check_scope: Scope) -> None:
        # Prevent cyclic inheritance by checking if the sup scope is already in the list.
        existing_sup_scope = [
            s for s in cls_symbol.scope.sup_scopes
            if (type(s._ast) is SupPrototypeExtensionAst) and s._ast is not self
                and AstTypeUtils.relaxed_symbolic_eq(self.name, s._ast.name, check_scope, s)
                and AstTypeUtils.symbolic_eq(s._ast.super_class, self.super_class, s, check_scope)]

        if existing_sup_scope and cls_symbol.name.value[0] != "$":
            raise SemanticErrors.SuperimpositionExtensionDuplicateSuperclassError().add(
                existing_sup_scope[0]._ast.super_class, self.super_class).scopes(check_scope)

    def _check_self_extension(self, cls_symbol: TypeSymbol, sup_symbol: TypeSymbol, check_scope: Scope) -> None:
        # Prevent self-inheritance by checking if the superimposition type is the same as the super type.
        # Todo: Should this comparison be done without generics? Because Vec[Str] extending Vec[BigInt] makes no sense.
        if AstTypeUtils.symbolic_eq(self.name, self.super_class, check_scope, check_scope):
            raise SemanticErrors.SuperimpositionExtensionSelfExtensionError().add(
                self.tok_ext).scopes(check_scope)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        if self.name.type_parts[0].value[0] == "$": return
        Asts.Ast.pre_process(self, ctx)
        generic_substitution = [Asts.GenericTypeArgumentNamedAst(pos=0, name=CommonTypes.Self(pos=0), value=self.name)]
        self.super_class = self.super_class.substituted_generics(generic_substitution)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a new scope for the superimposition.
        sm.create_and_move_into_new_scope(f"<sup#{self.name} ext {self.super_class}#{self.pos}>", self)
        Asts.Ast.generate_top_level_scopes(self, sm)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_optional_params():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(
                optional[0]).scopes(sm.current_scope)

        # Check every generic parameter is constrained by the type.
        if self.name.type_parts[0].value[0] != "$" and (unconstrained := [p for p in self.generic_parameter_group.parameters if not (self.name.contains_generic(p.name) or self.super_class.contains_generic(p.name))]):
            raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(
                unconstrained[0], self.name).scopes(sm.current_scope)

        # Ensure the superimposition type does not have a convention.
        if c := self.name.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.name, "superimposition type").scopes(sm.current_scope)

        # Ensure the superimposition supertype does not have a convention.
        if c := self.super_class.convention:
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
        self.body.generate_top_level_aliases(sm, **kwargs)
        sm.move_out_of_current_scope()

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.generic_parameter_group.qualify_types(sm, **kwargs)
        self.body.qualify_types(sm, **kwargs)
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        # Analyse the type being superimposed over.
        self.name.analyse_semantics(sm, **kwargs)
        self.name = sm.current_scope.get_symbol(self.name).fq_name

        # Register the superimposition against the base symbol.
        cls_symbol = sm.current_scope.get_symbol(self.name.without_generics)
        if sm.current_scope.parent is sm.current_scope.parent_module:
            if not cls_symbol.is_generic:
                sm.normal_sup_blocks[cls_symbol].append(sm.current_scope)
            else:
                sm.generic_sup_blocks[cls_symbol] = sm.current_scope

        # Add the "Self" symbol into the scope.
        if self.name.type_parts[0].value[0] != "$":
            cls_symbol = sm.current_scope.get_symbol(self.name)
            sm.current_scope.add_symbol(AliasSymbol(
                name=Asts.TypeIdentifierAst(value="Self"),
                type=None,
                scope=cls_symbol.scope,
                scope_defined_in=sm.current_scope,
                old_sym=cls_symbol))

        # Analyse the supertype after Self has been added (allows use in generic arguments to the superclass).
        self.super_class.analyse_semantics(sm, **kwargs)
        self.super_class = sm.current_scope.get_symbol(self.super_class).fq_name

        # Check the supertype is not generic.
        sup_symbol = sm.current_scope.get_symbol(self.super_class)
        if sup_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(
                self.super_class, self.super_class, "superimposition supertype").scopes(sm.current_scope)

        self.body.load_super_scopes(sm, **kwargs)
        sm.move_out_of_current_scope()

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Move to the next scope.
        sm.move_to_next_scope()
        self.name.analyse_semantics(sm, **kwargs)
        self.super_class.analyse_semantics(sm, **kwargs)
        cls_symbol = sm.current_scope.get_symbol(self.name)
        sup_symbol = sm.current_scope.get_symbol(self.super_class)

        # Mark the class as copyable if the "Copy" type is the super class.
        for sup_scope in [sup_symbol.scope] + sm.current_scope.get_symbol(self.super_class).scope.sup_scopes:
            if type(sup_scope._ast) is Asts.ClassPrototypeAst:
                fq_name = sup_scope.type_symbol.fq_name
                if AstTypeUtils.symbolic_eq(fq_name, CommonTypesPrecompiled.COPY, sup_scope, sm.current_scope):
                    sm.current_scope.get_symbol(self.name.without_generics).is_direct_copyable = True
                    cls_symbol.is_direct_copyable = True
                    break

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

                case Asts.SupTypeStatementAst():
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

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.body.check_memory(sm, **kwargs)
        sm.move_out_of_current_scope()

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        # Generate the LLVM code for the class implementation.
        sm.move_to_next_scope()
        self.body.code_gen_pass_1(sm, llvm_module, **kwargs)
        sm.move_out_of_current_scope()

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module = None, **kwargs) -> None:
        # Generate the LLVM code for the class implementation.
        sm.move_to_next_scope()
        self.body.code_gen_pass_2(sm, llvm_module, **kwargs)
        sm.move_out_of_current_scope()


__all__ = [
    "SupPrototypeExtensionAst"]
