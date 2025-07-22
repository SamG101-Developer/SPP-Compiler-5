from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastOrderedSet import FastOrderedSet
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class ObjectInitializerArgumentGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    arguments: list[Asts.ObjectInitializerArgumentAst] = field(default_factory=list)
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
        return arg.value if type(arg) is Asts.ObjectInitializerArgumentNamedAst else arg.name

    def get_default_arg(self) -> Optional[Asts.ObjectInitializerArgumentNamedAst]:
        args = [a for a in self.arguments if type(a) is Asts.ObjectInitializerArgumentUnnamedAst and a.is_default]
        return args[0] if args else None

    def get_regular_args(self) -> list[Asts.ObjectInitializerArgumentAst]:
        return [a for a in self.arguments if type(a) is not Asts.ObjectInitializerArgumentUnnamedAst or a.is_default is None]

    def get_named_args(self) -> list[Asts.ObjectInitializerArgumentNamedAst]:
        return [a for a in self.arguments if type(a) is Asts.ObjectInitializerArgumentNamedAst]

    def get_unnamed_args(self) -> list[Asts.ObjectInitializerArgumentUnnamedAst]:
        return [a for a in self.arguments if type(a) is Asts.ObjectInitializerArgumentUnnamedAst]

    def pre_analyse_semantics(self, sm: ScopeManager, class_type: Asts.TypeAst = None, **kwargs) -> None:
        # Get the symbol of the class type.
        class_symbol = sm.current_scope.get_symbol(class_type)

        # Get the attribute information from the class type.
        all_attributes = [(c, class_symbol.scope) for c in class_symbol.type.body.members]
        for sup_scope in class_symbol.scope.sup_scopes:
            if type(sup_scope._ast) is Asts.ClassPrototypeAst:
                all_attributes += [(c, sup_scope) for c in sup_scope._ast.body.members]

        for argument in self.arguments:

            # Return-type-overloading helper code.
            if type(argument) is Asts.ObjectInitializerArgumentNamedAst:
                if type(argument.value) is Asts.PostfixExpressionAst and type(argument.value.op) is Asts.PostfixExpressionOperatorFunctionCallAst:
                    attr = [(a, s) for a, s in all_attributes if a.name == argument.name]
                    attr_sym = attr[0][1].get_symbol(attr[0][0].type)
                    attr_type = attr_sym.fq_name if attr else None
                    kwargs |= {"inferred_return_type": attr_type if not attr_sym.is_generic else None}

            # Analyse the argument and enforce memory integrity.
            argument.analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, class_type: Asts.TypeAst = None, **kwargs) -> None:
        # Get the symbol of the class type.
        class_symbol = sm.current_scope.get_symbol(class_type)

        # Get the attribute information from the class type.
        all_attributes = [(c, class_symbol.scope) for c in class_symbol.type.body.members]
        for sup_scope in class_symbol.scope.sup_scopes:
            if type(sup_scope._ast) is Asts.ClassPrototypeAst:
                all_attributes += [(c, sup_scope) for c in sup_scope._ast.body.members]
        all_attribute_names = [a[0].name for a in all_attributes]

        # Check there are no duplicate argument names.
        argument_names = [a.name for a in self.get_regular_args()]
        if duplicates := SequenceUtils.duplicates(argument_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[1], "named object arguments").scopes(sm.current_scope)

        # Check there is at most 1 default argument.
        def_args = [a for a in self.arguments if type(a) is Asts.ObjectInitializerArgumentUnnamedAst and a.is_default]
        if len(def_args) > 1:
            raise SemanticErrors.ObjectInitializerMultipleDefArgumentsError().add(
                def_args[0], def_args[1]).scopes(sm.current_scope)

        # Check there are no invalidly named arguments.
        if invalid_arguments := FastOrderedSet(argument_names) - FastOrderedSet(all_attribute_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(
                self, "attribute", invalid_arguments.pop(0), "object initialization argument").scopes(sm.current_scope)

        # Type check the regular arguments against the class attributes.
        for argument in self.get_regular_args():

            # Todo: some sort of ambiguity check here? check if there is > 1 attribute with the same name.
            attribute, sup_scope = [a for a in all_attributes if a[0].name == argument.name][0]
            attribute_type = sup_scope.get_symbol(class_symbol.scope.get_symbol(attribute.name).type).fq_name
            argument_type = argument.infer_type(sm, **(kwargs | {"assignment_type": attribute_type}))

            if not AstTypeUtils.symbolic_eq(attribute_type, argument_type, sm.current_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    attribute, attribute_type, argument, argument_type).scopes(sm.current_scope)

        # Type check the default argument if it exists.
        def_argument = self.get_default_arg()
        def_argument_type = def_argument.name.infer_type(sm, **kwargs) if def_argument else None
        target_def_type = class_type
        if def_argument and not AstTypeUtils.symbolic_eq(def_argument_type, target_def_type, class_symbol.scope, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                class_type, target_def_type, def_argument.name, def_argument_type).scopes(sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        for argument in self.arguments:
            val = self.get_arg_val(argument)
            val.check_memory(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(
                val, argument, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
                check_pins=True, check_pins_linked=True, mark_moves=True, **kwargs)

        # Todo: what is this even doing?
        for argument in self.get_regular_args():
            for assign_target in kwargs.get("assignment", []):
                val = self.get_arg_val(argument)
                if sm.current_scope.get_symbol(val):
                    sm.current_scope.get_symbol(assign_target).memory_info.ast_pins.append(val)


__all__ = ["ObjectInitializerArgumentGroupAst"]
