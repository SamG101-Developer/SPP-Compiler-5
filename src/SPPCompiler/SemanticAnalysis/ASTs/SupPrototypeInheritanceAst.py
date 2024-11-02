from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import PreProcessingContext

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class SupPrototypeInheritanceAst(SupPrototypeFunctionsAst):
    tok_ext: TokenAst
    super_class: TypeAst

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, InnerScopeAst
        from SPPCompiler.SemanticAnalysis import WhereBlockAst, TokenAst

        # Create default instances.
        self.tok_sup = self.tok_sup or TokenAst.default(TokenType.KwSup)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.tok_ext = self.tok_ext or TokenAst.default(TokenType.KwExt)
        self.body = self.body or InnerScopeAst.default()

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

    def pre_process(self, context: PreProcessingContext) -> None:
        if self.name.types[-1].value[0] == "$": return
        super().pre_process(context)

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        scope_manager.move_to_next_scope()

        # print(self)

        # Get the class and super class symbols.
        self.super_class.analyse_semantics(scope_manager)
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class)

        # Cannot superimpose over a generic type.
        if cls_symbol.is_generic:
            raise AstErrors.INVALID_PLACE_FOR_GENERIC(self.name, "superimpose over a generic type")

        # Register the superimposition as a "sup scope", and the "sub scopes".
        cls_symbol.scope._direct_sup_scopes.append(scope_manager.current_scope)
        sup_symbol.scope._direct_sub_scopes.append(scope_manager.current_scope)
        sup_symbol.scope._direct_sub_scopes.append(cls_symbol.scope)

        # Mark the class as copyable if the Copy type is the super class.
        if self.super_class.symbolic_eq(CommonTypes.Copy(), scope_manager.current_scope):
            cls_symbol.is_copyable = True

        # Run the load steps for the body.
        self.body.load_sup_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions, FunctionConflictCheckType

        # Move to the next scope.
        scope_manager.move_to_next_scope()

        # Get the class and super class symbols.
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class)

        # Analyse the generic parameter group.
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)

        # Check every generic parameter is constrained by the type.
        if unconstrained := self.generic_parameter_group.parameters.filter(lambda p: not self.name.contains_generic(p.name)):
            raise AstErrors.SUP_UNCONSTRAINED_GENERIC_PARAMETER(unconstrained)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_opt():
            raise AstErrors.SUP_OPTIONAL_GENERIC_PARAMETER(optional[0])

        # Analyse the name, where block, and body.
        self.name.analyse_semantics(scope_manager, **kwargs)
        self.super_class.analyse_semantics(scope_manager, **kwargs)
        self.where_block.analyse_semantics(scope_manager, **kwargs)
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Check every member on the superimposition exists on the super class.
        # Todo: Add support for type aliasing in the superimposition.
        for member in self.body.members.filter_to_type(SupPrototypeInheritanceAst):
            this_method = member.body.members[-1]
            base_method = AstFunctions.check_for_conlicting_method(scope_manager, sup_symbol.scope, this_method, FunctionConflictCheckType.InvalidOverride)

            # Check the base method exists.
            if not base_method:
                raise AstErrors.SUP_MEMBER_INVALID(this_method, self.super_class)

            # Check the base method is virtual.
            if not base_method._virtual:
                raise AstErrors.SUP_MEMBER_NOT_VIRTUAL(this_method, self.super_class)

        # Check every abstract method on the super class is implemented.
        for base_method in cls_symbol.scope._direct_sup_scopes.map(lambda s: s._ast.body.members).flat():
            this_method = AstFunctions.check_for_conflicting_method(scope_manager, cls_symbol.scope, base_method, FunctionConflictCheckType.InvalidOverride)

            # Check the abstract methods are overridden.
            if base_method._abstract and not this_method:
                raise AstErrors.SUP_ABSTRACT_MEMBER_NOT_OVERRIDEN(base_method, self.name)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SupPrototypeInheritanceAst"]
