from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


# TODO
#  - Prevent abstract types being initialized (types with an abstract method)


@dataclass(slots=True)
class ObjectInitializerAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    class_type: Asts.TypeAst = field(default=None)
    object_argument_group: Asts.ObjectInitializerArgumentGroupAst = field(default=None)

    def __post_init__(self) -> None:
        self.object_argument_group = self.object_argument_group or Asts.ObjectInitializerArgumentGroupAst(pos=self.pos)
        assert self.class_type is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.object_argument_group.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.object_argument_group.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Use the type of the object initializer.
        return self.class_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Get the base symbol.
        base_symbol = sm.current_scope.get_symbol(self.class_type.without_generics())
        if not base_symbol:
            raise SemanticErrors.IdentifierUnknownError().add(
                self.class_type, "type", None).scopes(sm.current_scope)

        # Prevent generic types from being initialized.
        if base_symbol.is_generic:
            raise SemanticErrors.GenericTypeInvalidUsageError().add(
                self.class_type, self.class_type, "object initializer").scopes(sm.current_scope)

        self.object_argument_group.pre_analyse_semantics(sm, **kwargs)

        # Determine the generic inference source and target
        generic_infer_source = {
            a.name: self.object_argument_group.get_arg_val(a).infer_type(sm, **kwargs)
            for a in self.object_argument_group.arguments.filter(lambda a: isinstance(a.name, Asts.IdentifierAst))}

        generic_infer_target = {
            a.name: a.type
            for a in base_symbol.type.body.members}

        # Analyse the type and object argument group.
        base_symbol.type.body.analyse_semantics(ScopeManager(sm.current_scope, base_symbol.scope), **kwargs)
        self.class_type.analyse_semantics(sm, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)
        self.object_argument_group.analyse_semantics(sm, class_type=self.class_type, **kwargs)


__all__ = [
    "ObjectInitializerAst"]
