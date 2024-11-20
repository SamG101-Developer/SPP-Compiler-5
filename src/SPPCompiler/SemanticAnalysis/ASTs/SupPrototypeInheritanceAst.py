from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext

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

    def generate_symbols(self, scope_manager: ScopeManager, name_override: str = None) -> None:
        super().generate_symbols(scope_manager, name_override=f"<sup:{self.name} ext {self.super_class}:{self.pos}>")

    def load_sup_scopes(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        scope_manager.move_to_next_scope()

        self.super_class.analyse_semantics(scope_manager)
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class.without_generics())
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())

        # Cannot superimpose with a generic super class.
        if cls_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(self.name, self.name, "superimposition type")
        if sup_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(self.super_class, self.super_class, "superimposition supertype")

        # Register the superimposition as a "sup scope" and run the load steps for the body.
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class)
        cls_symbol.scope._direct_sup_scopes.append(scope_manager.current_scope)
        cls_symbol.scope._direct_sup_scopes.append(sup_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(cls_symbol.scope)
        sup_symbol.scope._direct_sub_scopes.append(scope_manager.current_scope)

        # Mark the class as copyable if the Copy type is the super class.
        if self.super_class.symbolic_eq(CommonTypes.Copy(), scope_manager.current_scope):
            cls_symbol.is_copyable = True

        # Run the inject steps for the body.
        self.body.load_sup_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        self.super_class.analyse_semantics(scope_manager)
        self.body.regenerate_generic_types(scope_manager)
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions, FunctionConflictCheckType

        # Todo: Check the same superclass isn't extended twice.
        # Todo: Add support for type aliasing in the superimposition.

        # Move to the next scope.
        scope_manager.move_to_next_scope()

        # Get the class and super class symbols.
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())
        sup_symbol = scope_manager.current_scope.get_symbol(self.super_class)

        # Analyse the generic parameter group.
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)

        # Check every generic parameter is constrained by the type.
        if unconstrained := self.generic_parameter_group.parameters.filter(lambda p: not self.name.contains_generic(p.name)):
            if not self.name.types[-1].value.startswith("$"):
                raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(unconstrained[0], self.name)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_opt():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(optional[0])

        # Analyse the name, where block, and body.
        self.name.analyse_semantics(scope_manager, **kwargs)
        self.super_class.analyse_semantics(scope_manager, **kwargs)
        self.where_block.analyse_semantics(scope_manager, **kwargs)
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Check every member on the superimposition exists on the super class.
        for member in self.body.members.filter_to_type(SupPrototypeInheritanceAst):
            this_method = member.body.members[-1]
            base_method = AstFunctions.check_for_conflicting_method(scope_manager.current_scope, sup_symbol.scope, this_method, FunctionConflictCheckType.InvalidOverride)

            # Check the base method exists.
            if not base_method:
                raise SemanticErrors.SuperimpositionInheritanceMethodInvalidError().add(this_method.name, self.super_class)

            # Check the base method is virtual or abstract.
            if not (base_method._virtual or base_method._abstract):
                raise SemanticErrors.SuperimpositionInheritanceNonVirtualMethodOverriddenError().add(base_method.name, self.super_class)

        # Check every abstract method on the super class is implemented.
        for base_member in sup_symbol.scope._direct_sup_scopes.filter(lambda s: isinstance(s._ast, SupPrototypeFunctionsAst)).map(lambda s: s._ast.body.members).flat().filter_to_type(SupPrototypeInheritanceAst):
            base_method = base_member.body.members[-1]
            this_method = AstFunctions.check_for_conflicting_method(sup_symbol.scope, scope_manager.current_scope, base_method, FunctionConflictCheckType.InvalidOverride)

            # Check the abstract methods are overridden.
            if base_method._abstract and not this_method:
                raise SemanticErrors.SuperimpositionInheritanceAbstractMethodNotOverriddenError().add(base_method.name, self.super_class)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SupPrototypeInheritanceAst"]
