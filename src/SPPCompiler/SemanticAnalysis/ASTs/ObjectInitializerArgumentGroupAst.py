from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ObjectInitializerArgumentGroupAst(Ast):
    tok_left_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenL))
    arguments: Seq[Asts.ObjectInitializerArgumentAst] = field(default_factory=Seq)
    tok_right_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenR))

    def __copy__(self) -> ObjectInitializerArgumentGroupAst:
        # Create a shallow copy of the AST.
        return ObjectInitializerArgumentGroupAst(arguments=self.arguments.copy())

    @std.override_method
    def __eq__(self, other: ObjectInitializerArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, ObjectInitializerArgumentGroupAst) and self.arguments == other.arguments

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.arguments.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    def get_arg_val(self, argument: Asts.ObjectInitializerArgumentAst) -> Asts.ExpressionAst:
        return argument.value if isinstance(argument, Asts.ObjectInitializerArgumentNamedAst) else argument.name

    def get_def_args(self) -> Seq[Asts.ObjectInitializerArgumentNamedAst]:
        return self.arguments.filter_to_type(Asts.ObjectInitializerArgumentUnnamedAst).filter(lambda a: a.is_default is not None)

    def get_val_args(self) -> Seq[Asts.ObjectInitializerArgumentAst]:
        return self.arguments.filter(lambda a: not isinstance(a, Asts.ObjectInitializerArgumentUnnamedAst) or a.is_default is None)

    def pre_analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the arguments and enforce memory integrity.
        for argument in self.arguments:
            argument.analyse_semantics(scope_manager, **kwargs)
            AstMemoryHandler.enforce_memory_integrity(self.get_arg_val(argument), argument, scope_manager)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, class_type: Asts.TypeAst = None, **kwargs) -> None:
        # Get the symbol of the class type, and check it isn't abstract.
        class_symbol = scope_manager.current_scope.get_symbol(class_type)
        # if class_symbol.is_abstract:
        #     raise SemanticErrors.ObjectInitializerAbstractClassError().add(class_type)

        # Get the attribute information from the class type.
        all_attributes = Seq([(c, class_symbol.scope) for c in class_symbol.type.body.members])
        for sup_scope in class_symbol.scope.sup_scopes.filter(lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)):
            all_attributes += [(c, sup_scope) for c in sup_scope._ast.body.members]
        all_attribute_names = all_attributes.map(lambda x: x[0].name)

        # Check there are no duplicate argument names.
        argument_names = self.get_val_args().map(lambda a: a.name)
        if duplicates := argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "named object arguments")

        # Check there is at most 1 default argument.
        if (default_arguments := self.get_def_args()).length > 1:
            raise SemanticErrors.ObjectInitializerMultipleDefArgumentsError().add(default_arguments[0], default_arguments[1])
        def_argument = self.get_def_args().first()

        # Check there are no invalidly named arguments.
        if invalid_arguments := argument_names.set_subtract(all_attribute_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(self, "attribute", invalid_arguments[0], "object initialization argument")

        # Type check the regular arguments against the class attributes.
        for argument in self.get_val_args():
            attribute, sup_scope = all_attributes.find(lambda x: x[0].name == argument.name)
            argument_type = argument.infer_type(scope_manager, **kwargs)
            attribute_type = InferredType.from_type(attribute.type)

            if not attribute_type.symbolic_eq(argument_type, sup_scope, scope_manager.current_scope):
                raise SemanticErrors.TypeMismatchError().add(attribute, attribute_type, argument, argument_type)

        # Type check the default argument if it exists.
        def_argument_type = def_argument.name.infer_type(scope_manager, **kwargs) if def_argument else None
        target_def_type = InferredType.from_type(class_type)
        if def_argument and not def_argument_type.symbolic_eq(target_def_type, class_symbol.scope, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(class_type, target_def_type, def_argument.name, def_argument_type)


__all__ = ["ObjectInitializerArgumentGroupAst"]
