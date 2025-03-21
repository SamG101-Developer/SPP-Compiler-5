from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ObjectInitializerArgumentGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    arguments: Seq[Asts.ObjectInitializerArgumentAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    def __copy__(self) -> ObjectInitializerArgumentGroupAst:
        # Create a shallow copy of the AST.
        return ObjectInitializerArgumentGroupAst(arguments=self.arguments.copy())

    def __eq__(self, other: ObjectInitializerArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, ObjectInitializerArgumentGroupAst) and self.arguments == other.arguments

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            self.arguments.print(printer, ", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def get_arg_val(self, arg: Asts.ObjectInitializerArgumentAst) -> Asts.ExpressionAst:
        return arg.value if isinstance(arg, Asts.ObjectInitializerArgumentNamedAst) else arg.name

    def get_default_args(self) -> Seq[Asts.ObjectInitializerArgumentNamedAst]:
        return self.arguments.filter_to_type(Asts.ObjectInitializerArgumentUnnamedAst).filter(lambda a: a.is_default is not None)

    def get_regular_args(self) -> Seq[Asts.ObjectInitializerArgumentAst]:
        return self.arguments.filter(lambda a: not isinstance(a, Asts.ObjectInitializerArgumentUnnamedAst) or a.is_default is None)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the arguments and enforce memory integrity.
        for argument in self.arguments:
            argument.analyse_semantics(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(self.get_arg_val(argument), argument, sm)

    def analyse_semantics(self, sm: ScopeManager, class_type: Asts.TypeAst = None, **kwargs) -> None:
        # Get the symbol of the class type, and check it isn't abstract.
        class_symbol = sm.current_scope.get_symbol(class_type)
        # if class_symbol.is_abstract:
        #     raise SemanticErrors.ObjectInitializerAbstractClassError().add(class_type).scopes(scope_manager.current_scope)

        # Get the attribute information from the class type.
        all_attributes = Seq([(c, class_symbol.scope) for c in class_symbol.type.body.members])
        for sup_scope in class_symbol.scope.sup_scopes.filter(lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)):
            all_attributes += [(c, sup_scope) for c in sup_scope._ast.body.members]
        all_attribute_names = all_attributes.map(lambda x: x[0].name)

        # Check there are no duplicate argument names.
        argument_names = self.get_regular_args().map(lambda a: a.name)
        if duplicates := argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0][0], duplicates[0][1], "named object arguments").scopes(sm.current_scope)

        # Check there is at most 1 default argument.
        if (default_arguments := self.get_default_args()).length > 1:
            raise SemanticErrors.ObjectInitializerMultipleDefArgumentsError().add(
                default_arguments[0], default_arguments[1]).scopes(sm.current_scope)
        def_argument = self.get_default_args().first()

        # Check there are no invalidly named arguments.
        if invalid_arguments := argument_names.set_subtract(all_attribute_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(
                self, "attribute", invalid_arguments[0], "object initialization argument").scopes(sm.current_scope)

        # Type check the regular arguments against the class attributes.
        for argument in self.get_regular_args():
            attribute, sup_scope = all_attributes.find(lambda x: x[0].name == argument.name)
            attribute_type = class_symbol.scope.get_symbol(attribute.name).type
            argument_type = argument.infer_type(sm, **kwargs)

            if not attribute_type.symbolic_eq(argument_type, sup_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    attribute, attribute_type, argument, argument_type).scopes(sm.current_scope)

        # Type check the default argument if it exists.
        target_def_type = class_type
        def_argument_type = def_argument.name.infer_type(sm, **kwargs) if def_argument else None
        if def_argument and not def_argument_type.symbolic_eq(target_def_type, class_symbol.scope, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                class_type, target_def_type, def_argument.name, def_argument_type).scopes(sm.current_scope)


__all__ = ["ObjectInitializerArgumentGroupAst"]
