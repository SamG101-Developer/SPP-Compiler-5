from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ObjectInitializerArgumentGroupAst import ObjectInitializerArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ObjectInitializerAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    class_type: TypeAst
    object_argument_group: ObjectInitializerArgumentGroupAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.object_argument_group.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Use the type of the object initializer.
        return InferredType.from_type(self.class_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Get the base symbol and make sure it isn't generic.
        base_symbol = scope_manager.current_scope.get_symbol(self.class_type.without_generics())
        if base_symbol.is_generic:
            raise AstErrors.INVALID_PLACE_FOR_GENERIC()

        # Determine the generic inference source and target
        generic_infer_source = {
            a.name: self.object_argument_group.get_arg_val(a) for a in self.object_argument_group.arguments.filter(lambda a: isinstance(a.name, IdentifierAst))}
        generic_infer_target = {
            a.name: a.type for a in base_symbol.type.body.members}

        # Analyse the type and object argument group.
        self.class_type.analyse_semantics(scope_manager, generic_infer_source, generic_infer_target, **kwargs)
        self.object_argument_group.analyse_semantics(scope_manager, class_type=self.class_type, **kwargs)


__all__ = ["ObjectInitializerAst"]
