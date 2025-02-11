from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


# TODO
#  - Prevent abstract types being initialized (types with an abstract method)


@dataclass
class ObjectInitializerAst(Ast, TypeInferrable):
    class_type: Asts.TypeAst = field(default=None)
    object_argument_group: Asts.ObjectInitializerArgumentGroupAst = field(default_factory=lambda: Asts.ObjectInitializerArgumentGroupAst())

    def __post_init__(self) -> None:
        assert self.class_type

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.object_argument_group.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Use the type of the object initializer.
        return self.class_type

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:

        # Check the type has no convention.
        if type(self.class_type.convention) is not Asts.ConventionMovAst:
            raise SemanticErrors.ConventionInvalidUsageError().add(self.class_type)

        # Get the base symbol and make sure it isn't generic.
        base_symbol = scope_manager.current_scope.get_symbol(self.class_type.without_generics())
        if base_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(self.class_type, self.class_type, "object initializer")

        self.object_argument_group.pre_analyse_semantics(scope_manager, **kwargs)

        # Determine the generic inference source and target
        generic_infer_source = {
            a.name: self.object_argument_group.get_arg_val(a).infer_type(scope_manager, **kwargs)
            for a in self.object_argument_group.arguments.filter(lambda a: isinstance(a.name, Asts.IdentifierAst))}
        generic_infer_target = {
            a.name: a.type
            for a in base_symbol.type.body.members}

        # Analyse the type and object argument group.
        base_symbol.type.body.analyse_semantics(ScopeManager(scope_manager.current_scope, base_symbol.scope), **kwargs)
        self.class_type.analyse_semantics(scope_manager, generic_infer_source, generic_infer_target, **kwargs)
        self.object_argument_group.analyse_semantics(scope_manager, class_type=self.class_type, **kwargs)


__all__ = ["ObjectInitializerAst"]
