from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class ObjectInitializerAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    class_type: Asts.TypeAst = field(default=None)
    object_argument_group: Asts.ObjectInitializerArgumentGroupAst = field(default=None)

    def __post_init__(self) -> None:
        self.object_argument_group = self.object_argument_group or Asts.ObjectInitializerArgumentGroupAst(pos=self.pos)

    def __eq__(self, other: ObjectInitializerAst) -> bool:
        # Check there are the same attribute keys on both objects, then compare the expressions on them (might be in a different order). Todo
        return False

    def __hash__(self) -> int:
        return id(self)

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
        return sm.current_scope.get_symbol(self.class_type).fq_name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Get the base symbol.
        base_symbol = sm.current_scope.get_symbol(self.class_type.without_generics)
        if not base_symbol:
            raise SemanticErrors.IdentifierUnknownError().add(
                self.class_type, "type", None).scopes(sm.current_scope)

        # Generic types cannot have any attributes set (full default initialization only).
        if base_symbol.is_generic:
            if self.object_argument_group.arguments:
                raise SemanticErrors.ObjectInitializerGenericWithArgumentsError().add(
                    self.class_type, self.object_argument_group.arguments[0]).scopes(sm.current_scope)
            return

        self.object_argument_group.pre_analyse_semantics(sm, class_type=self.class_type.without_generics, **kwargs)

        # Determine the generic inference source and target.
        generic_infer_source = {
            a.name: self.object_argument_group.get_arg_val(a).infer_type(sm, **kwargs)
            for a in self.object_argument_group.arguments
            if type(a.name) is Asts.IdentifierAst}  # todo: why constrain to IdentifierAst?

        generic_infer_target = {
            a.name: base_symbol.scope.get_symbol(a.type).fq_name
            for a in base_symbol.type.body.members}

        # Analyse the type and object argument group.
        base_symbol.type.body.analyse_semantics(ScopeManager(sm.current_scope, base_symbol.scope, nsbs=sm.normal_sup_blocks, gsbs=sm.generic_sup_blocks), **kwargs)
        self.class_type.analyse_semantics(sm, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)
        self.object_argument_group.analyse_semantics(sm, class_type=self.class_type, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Check the memory of the object argument group.
        self.object_argument_group.check_memory(sm, **kwargs)


__all__ = [
    "ObjectInitializerAst"]
