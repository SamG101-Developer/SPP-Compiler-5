from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ordered_set import OrderedSet

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
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

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.arguments, sep=", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def get_arg_val(self, arg: Asts.ObjectInitializerArgumentAst) -> Asts.ExpressionAst:
        return arg.value if isinstance(arg, Asts.ObjectInitializerArgumentNamedAst) else arg.name

    def get_default_arg(self) -> Optional[Asts.ObjectInitializerArgumentNamedAst]:
        args = [a for a in self.arguments if isinstance(a, Asts.ObjectInitializerArgumentUnnamedAst) and a.is_default]
        return args[0] if args else None

    def get_regular_args(self) -> Seq[Asts.ObjectInitializerArgumentAst]:
        return [a for a in self.arguments if not isinstance(a, Asts.ObjectInitializerArgumentUnnamedAst) or a.is_default is None]

    def get_named_args(self) -> Seq[Asts.ObjectInitializerArgumentNamedAst]:
        return [a for a in self.arguments if isinstance(a, Asts.ObjectInitializerArgumentNamedAst)]

    def get_unnamed_args(self) -> Seq[Asts.ObjectInitializerArgumentUnnamedAst]:
        return [a for a in self.arguments if isinstance(a, Asts.ObjectInitializerArgumentUnnamedAst)]

    def pre_analyse_semantics(self, sm: ScopeManager, class_type: Asts.TypeAst = None, **kwargs) -> None:
        # Get the symbol of the class type.
        class_symbol = sm.current_scope.get_symbol(class_type)

        # Get the attribute information from the class type.
        all_attributes = [(c, class_symbol.scope) for c in class_symbol.type.body.members]
        for sup_scope in class_symbol.scope.sup_scopes:
            if isinstance(sup_scope._ast, Asts.ClassPrototypeAst):
                all_attributes += [(c, sup_scope) for c in sup_scope._ast.body.members]

        for argument in self.arguments:

            # Return-type-overloading helper code.
            if isinstance(argument, Asts.ObjectInitializerArgumentNamedAst):
                if isinstance(argument.value, Asts.PostfixExpressionAst) and isinstance(argument.value.op, Asts.PostfixExpressionOperatorFunctionCallAst):
                    attr = [(a, s) for a, s in all_attributes if a.name == argument.name]
                    attr_sym = attr[0][1].get_symbol(attr[0][0].type)
                    attr_type = attr_sym.fq_name if attr else None
                    kwargs |= {"inferred_return_type": attr_type if not attr_sym.is_generic else None}

            # Analyse the argument and enforce memory integrity.
            argument.analyse_semantics(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(self.get_arg_val(argument), argument, sm)

    def analyse_semantics(self, sm: ScopeManager, class_type: Asts.TypeAst = None, **kwargs) -> None:
        # Get the symbol of the class type.
        class_symbol = sm.current_scope.get_symbol(class_type)

        # Get the attribute information from the class type.
        all_attributes = [(c, class_symbol.scope) for c in class_symbol.type.body.members]
        for sup_scope in class_symbol.scope.sup_scopes:
            if isinstance(sup_scope._ast, Asts.ClassPrototypeAst):
                all_attributes += [(c, sup_scope) for c in sup_scope._ast.body.members]
        all_attribute_names = [a[0].name for a in all_attributes]

        # Check there are no duplicate argument names.
        argument_names = [a.name for a in self.get_regular_args()]
        if duplicates := SequenceUtils.duplicates(argument_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[1], "named object arguments").scopes(sm.current_scope)

        # Check there is at most 1 default argument.
        def_args = [a for a in self.arguments if isinstance(a, Asts.ObjectInitializerArgumentUnnamedAst) and a.is_default]
        if len(def_args) > 1:
            raise SemanticErrors.ObjectInitializerMultipleDefArgumentsError().add(
                def_args[0], def_args[1]).scopes(sm.current_scope)

        # Check there are no invalidly named arguments.
        if invalid_arguments := OrderedSet(argument_names) - OrderedSet(all_attribute_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(
                self, "attribute", invalid_arguments.pop(0), "object initialization argument").scopes(sm.current_scope)

        # Type check the regular arguments against the class attributes.
        for argument in self.get_regular_args():
            attribute, sup_scope = [a for a in all_attributes if a[0].name == argument.name][0]
            attribute_type = class_symbol.scope.get_symbol(attribute.name).type
            argument_type = argument.infer_type(sm, **kwargs)

            if not attribute_type.symbolic_eq(argument_type, sup_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    attribute, attribute_type, argument, argument_type).scopes(sm.current_scope)

        # Type check the default argument if it exists.
        def_argument = self.get_default_arg()
        def_argument_type = def_argument.name.infer_type(sm, **kwargs) if def_argument else None
        target_def_type = class_type
        if def_argument and not def_argument_type.symbolic_eq(target_def_type, class_symbol.scope, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                class_type, target_def_type, def_argument.name, def_argument_type).scopes(sm.current_scope)


__all__ = ["ObjectInitializerArgumentGroupAst"]
