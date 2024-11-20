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
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import ObjectInitializerArgumentNamedAst, TokenAst

        # Filter the arguments to token arguments that are "else=".
        named_args = self.arguments.filter_to_type(ObjectInitializerArgumentNamedAst)
        token_args = named_args.filter(lambda arg: isinstance(arg.name, TokenAst))
        return token_args.filter(lambda arg: arg.name.token.token_type == TokenType.KwElse)

    def get_sup_args(self) -> Seq[ObjectInitializerArgumentNamedAst]:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import ObjectInitializerArgumentNamedAst, TokenAst

        # Filter the arguments to token arguments that are "sup=".
        named_args = self.arguments.filter_to_type(ObjectInitializerArgumentNamedAst)
        token_args = named_args.filter(lambda arg: isinstance(arg.name, TokenAst))
        return token_args.filter(lambda arg: arg.name.token.token_type == TokenType.KwSup)

    def get_val_args(self) -> Seq[ObjectInitializerArgumentAst]:
        from SPPCompiler.SemanticAnalysis import TokenAst

        # Filter the arguments to non-token arguments.
        return self.arguments.filter(lambda arg: not isinstance(arg.name, TokenAst))

    def pre_analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler

        # Analyse the arguments and enforce memory integrity.
        for argument in self.arguments:
            argument.analyse_semantics(scope_manager, **kwargs)
            AstMemoryHandler.enforce_memory_integrity(self.get_arg_val(argument), argument, scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, class_type: TypeAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import IdentifierAst, ClassPrototypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType

        # Get symbol and attribute information from the class type.
        class_symbol = scope_manager.current_scope.get_symbol(class_type)
        attributes = class_symbol.type.body.members
        attribute_names = attributes.map_attr("name")
        super_classes = class_symbol.scope._direct_sup_scopes.filter(lambda s: isinstance(s._ast, ClassPrototypeAst)).map(lambda s: s.type_symbol.fq_name)

        # Check there are no duplicate argument names.
        argument_names = self.get_val_args().map(lambda a: a.name)
        if duplicates := argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "named object arguments")

        # Check there is at most 1 default argument.
        if self.get_def_args().length > 1:
            default_arguments = self.get_def_args()
            raise SemanticErrors.ObjectInitializerMultipleSupArgumentsError().add(default_arguments[0], default_arguments[1])
        def_argument = self.get_def_args().first()

        # Check there is at most 1 super argument.
        if self.get_sup_args().length > 1:
            sup_arguments = self.get_sup_args()
            raise SemanticErrors.ObjectInitializerMultipleSupArgumentsError().add(sup_arguments[0], sup_arguments[1])
        sup_argument = self.get_sup_args().first()

        # Check every attribute has been assigned a value (unless the default argument is present).
        if not def_argument and (missing_attributes := attribute_names.set_subtract(argument_names)):
            raise SemanticErrors.ArgumentRequiredNameMissingError().add(self, missing_attributes[0], "attribute", "object initialization argument")

        # Check there are no invalidly named arguments.
        if invalid_arguments := argument_names.set_subtract(attribute_names):
            missing_arguments = attribute_names.set_subtract(argument_names)
            raise SemanticErrors.ArgumentNameInvalidError().add(missing_arguments[0], "attribute", invalid_arguments[0], "object initialization argument")

        # Type check the regular arguments against the class attributes.
        sorted_arguments = self.arguments.filter(lambda a: isinstance(a.name, IdentifierAst)).sort(key=lambda a: attribute_names.index(a.name))
        for argument, attribute in sorted_arguments.zip(attributes):
            argument_type = argument.infer_type(scope_manager, **kwargs)
            attribute_type = InferredType.from_type(attribute.type)

            if not attribute_type.symbolic_eq(argument_type, class_symbol.scope, scope_manager.current_scope):
                raise SemanticErrors.TypeMismatchError().add(attribute, attribute_type, argument, argument_type)

        # Type check the default argument if it exists.
        def_argument_type = def_argument.value.infer_type(scope_manager, **kwargs) if def_argument else None
        target_def_type = InferredType.from_type(class_type)
        if def_argument and not def_argument_type.symbolic_eq(target_def_type, class_symbol.scope, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(class_type, target_def_type, def_argument, def_argument_type)

        # Check the "sup=" argument provides a tuple.
        sup_argument_type = sup_argument.value.infer_type(scope_manager, **kwargs) if sup_argument else None
        target_sup_type = InferredType.from_type(CommonTypes.Tup().without_generics())
        if sup_argument and not sup_argument_type.without_generics().symbolic_eq(target_sup_type, class_symbol.scope, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(class_type, target_sup_type, sup_argument, sup_argument_type)

        if sup_argument:
            # Todo: Switch comparisons to symbolic_eq (remove fq_name)
            given_sup_types = sup_argument_type.type.types[-1].generic_argument_group.arguments.map_attr("value")
            given_sup_types = given_sup_types.map(lambda s: scope_manager.current_scope.get_symbol(s).fq_name)

            # Check if there are any missing types in the "sup=" tuple.
            if sup_argument and (missing_superclasses := super_classes.set_subtract(given_sup_types)):
                raise SemanticErrors.ArgumentRequiredNameMissingError().add(self, missing_superclasses[0], "superclass", "object initialization sup argument")

            # Check if there are any extra invalid types in the "sup=" tuple.
            if sup_argument and (invalid_superclasses := given_sup_types.set_subtract(super_classes)):
                missing_superclasses = super_classes.set_subtract(given_sup_types)
                raise SemanticErrors.ArgumentNameInvalidError().add(missing_superclasses[0], "superclass", invalid_superclasses[0], "object initialization sup argument")


__all__ = ["ObjectInitializerArgumentGroupAst"]
