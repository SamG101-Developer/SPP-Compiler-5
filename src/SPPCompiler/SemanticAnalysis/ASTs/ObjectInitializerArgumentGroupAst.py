from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.ObjectInitializerArgumentAst import ObjectInitializerArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.ObjectInitializerArgumentNamedAst import ObjectInitializerArgumentNamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ObjectInitializerArgumentGroupAst(Ast, CompilerStages):
    tok_left_paren: TokenAst
    arguments: Seq[ObjectInitializerArgumentAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the arguments into a sequence.
        self.arguments = Seq(self.arguments)

    def __copy__(self) -> ObjectInitializerArgumentGroupAst:
        # Create a shallow copy of the AST.
        return ObjectInitializerArgumentGroupAst.default(self.arguments.copy())

    def __eq__(self, other: ObjectInitializerArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, ObjectInitializerArgumentGroupAst) and self.arguments == other.arguments

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.arguments.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @staticmethod
    def default(arguments: Seq[ObjectInitializerArgumentAst]) -> ObjectInitializerArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return ObjectInitializerArgumentGroupAst(-1, TokenAst.default(TokenType.TkParenL), arguments or Seq(), TokenAst.default(TokenType.TkParenR))

    @staticmethod
    def get_arg_val(argument: ObjectInitializerArgumentAst) -> ExpressionAst:
        from SPPCompiler.SemanticAnalysis import ObjectInitializerArgumentNamedAst
        return argument.value if isinstance(argument, ObjectInitializerArgumentNamedAst) else argument.name

    def get_def_args(self) -> Seq[ObjectInitializerArgumentNamedAst]:
        from SPPCompiler.SemanticAnalysis import ObjectInitializerArgumentUnnamedAst
        return self.arguments.filter_to_type(ObjectInitializerArgumentUnnamedAst).filter(lambda a: a.is_default is not None)

    def get_val_args(self) -> Seq[ObjectInitializerArgumentAst]:
        from SPPCompiler.SemanticAnalysis import ObjectInitializerArgumentUnnamedAst
        return self.arguments.filter(lambda a: not isinstance(a, ObjectInitializerArgumentUnnamedAst) or a.is_default is None)

    def pre_analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler

        # Analyse the arguments and enforce memory integrity.
        for argument in self.arguments:
            argument.analyse_semantics(scope_manager, **kwargs)
            AstMemoryHandler.enforce_memory_integrity(self.get_arg_val(argument), argument, scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, class_type: TypeAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import ClassPrototypeAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType

        # Get the symbol of the class type, and check it isn't abstract.
        class_symbol = scope_manager.current_scope.get_symbol(class_type)
        # if class_symbol.is_abstract:
        #     raise SemanticErrors.ObjectInitializerAbstractClassError().add(class_type)

        # Get the attribute information from the class type.
        all_attributes = Seq([(c, class_symbol.scope) for c in class_symbol.type.body.members])
        for sup_scope in class_symbol.scope.sup_scopes.filter(lambda s: isinstance(s._ast, ClassPrototypeAst)):
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
