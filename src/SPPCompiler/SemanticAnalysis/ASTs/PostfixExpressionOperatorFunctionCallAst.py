from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional, Tuple

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class PostfixExpressionOperatorFunctionCallAst(Ast, TypeInferrable):
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default_factory=Asts.GenericArgumentGroupAst)
    function_argument_group: Asts.FunctionCallArgumentGroupAst = field(default_factory=Asts.FunctionCallArgumentGroupAst)
    fold_token: Optional[Asts.TokenAst] = field(default=None)

    _overload: Optional[Tuple[Scope, Asts.FunctionPrototypeAst]] = field(default=None, init=False, repr=False)
    _is_async: Optional[Ast] = field(default=None, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.generic_argument_group.print(printer),
            self.function_argument_group.print(printer),
            self.fold_token.print(printer) if self.fold_token else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.function_argument_group.pos_end

    def determine_overload(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # 3 types of function calling: function_call(), obj.method_call(), Type::static_method_call(). Determine the
        # function's name and its owner type/namespace.

        # Todo: Change this to detecting FunMov/Mut/Ref superimpositions over the type
        function_owner_type, function_owner_scope, function_name = AstFunctions.get_function_owner_type_and_function_name(scope_manager, lhs)
        if not function_name:
            raise SemanticErrors.FunctionCallOnNoncallableTypeError().add(lhs).scopes(scope_manager.current_scope)

        # Convert the obj.method_call(...args) into Type::method_call(obj, ...args).
        if isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_runtime_access():
            transformed_lhs, transformed_function_call = AstFunctions.convert_method_to_function_form(scope_manager, function_owner_type, function_name, lhs, self)
            transformed_function_call.determine_overload(scope_manager, transformed_lhs, **kwargs)
            self._overload = transformed_function_call._overload
            self.function_argument_group = transformed_function_call.function_argument_group
            return

        # Record the "pass" and "fail" overloads
        all_overloads = AstFunctions.get_all_function_scopes(function_name, function_owner_scope)
        pass_overloads = Seq()
        fail_overloads = Seq()

        for function_scope, function_overload, owner_scope_generic_arguments in all_overloads:
            owner_scope_generic_arguments = owner_scope_generic_arguments.arguments

            # Extract generic/function parameter information from the overload.
            parameters = function_overload.function_parameter_group.parameters.copy()
            parameter_names = parameters.map_attr("extract_name")
            parameter_names_req = function_overload.function_parameter_group.get_req().map_attr("extract_name")
            generic_parameters = function_overload.generic_parameter_group.parameters
            is_variadic = function_overload.function_parameter_group.get_var() is not None

            # Extract generic/function argument information from this AST.
            arguments = self.function_argument_group.arguments.copy()
            argument_names = arguments.filter_to_type(Asts.FunctionCallArgumentNamedAst).map_attr("name")
            generic_arguments = self.generic_argument_group.arguments.copy()

            # Use a try-except block to catch any errors as a following overload could still be valid.
            try:
                # Can't call an abstract function.
                if function_overload._abstract:
                    raise SemanticErrors.FunctionCallAbstractFunctionError().add(function_overload.name, self).scopes(scope_manager.current_scope)

                # Can't call non-implemented functions (dummy functions).
                if function_overload._non_implemented:
                    ...  # Todo: raise SemanticErrors.FunctionCallNonImplementedMethodError

                # Check if there are too many arguments for the function (non-variadic).
                if arguments.length > parameters.length and not is_variadic:
                    raise SemanticErrors.FunctionCallTooManyArgumentsError().add(self, function_overload.name).scopes(scope_manager.current_scope)

                # Check for any named arguments without a corresponding parameter.
                # Todo: Generic=Void means the associated parameters should be removed.
                if invalid_arguments := argument_names.set_subtract(parameter_names):
                    raise SemanticErrors.ArgumentNameInvalidError().add(parameters[0], "parameter", invalid_arguments[0], "argument").scopes(scope_manager.current_scope)

                # Remove all the used parameters names from the set of parameter names, and name the unnamed arguments.
                AstFunctions.name_function_arguments(arguments, parameters, scope_manager)
                AstFunctions.name_generic_arguments(generic_arguments, generic_parameters, scope_manager)
                argument_names = arguments.map_attr("name")

                # Check if there are too few arguments for the function (by missing names).
                if missing_parameters := parameter_names_req.set_subtract(argument_names):
                    raise SemanticErrors.ArgumentRequiredNameMissingError().add(self, missing_parameters[0], "parameter", "argument")

                # Infer generic arguments and inherit from the function owner block.
                generic_arguments = AstFunctions.infer_generic_arguments(
                    generic_parameters=function_overload.generic_parameter_group.get_req(),
                    explicit_generic_arguments=generic_arguments + owner_scope_generic_arguments,
                    infer_source=arguments.map(lambda a: (a.name, a.infer_type(scope_manager, **kwargs))).dict(),
                    infer_target=parameters.map(lambda p: (p.extract_name, p.type)).dict(),
                    scope_manager=scope_manager, owner=lhs,
                    variadic_parameter_identifier=function_overload.function_parameter_group.get_var().extract_name if is_variadic else None)

                # Create a new overload with the generic arguments applied.
                if generic_arguments:
                    temp_manager = ScopeManager(scope_manager.global_scope, function_scope)

                    new_overload = copy.deepcopy(function_overload)
                    new_overload.generic_parameter_group.parameters = Seq()
                    for p in new_overload.function_parameter_group.parameters:
                        p.type = p.type.sub_generics(generic_arguments)
                    for p in new_overload.function_parameter_group.parameters:
                        p.type.analyse_semantics(temp_manager, **kwargs)
                    new_overload.return_type = new_overload.return_type.sub_generics(generic_arguments)
                    new_overload.return_type.analyse_semantics(temp_manager, **kwargs)

                    parameters = new_overload.function_parameter_group.parameters.copy()
                    function_overload = new_overload
                    function_scope = temp_manager.current_scope

                # Type check the arguments against the parameters.
                sorted_arguments = arguments.sort(key=lambda a: parameter_names.index(a.name))
                for argument, parameter in sorted_arguments.zip(parameters):
                    parameter_type = parameter.type
                    argument_type = argument.infer_type(scope_manager, **kwargs)

                    if isinstance(parameter, Asts.FunctionParameterVariadicAst):
                        parameter_type = CommonTypes.Tup(Seq([parameter_type] * argument_type.type_parts()[0].generic_argument_group.arguments.length))
                        parameter_type.analyse_semantics(scope_manager, **kwargs)

                    if isinstance(parameter, Asts.FunctionParameterSelfAst):
                        argument.convention = parameter.convention
                        argument_type = argument_type.without_generics()

                        # if function_overload.function_parameter_group.get_self()._arbitrary and not parameter_type.without_generics().without_convention().symbolic_eq(argument_type.without_generics(), function_scope, scope_manager.current_scope, debug=True):
                        #     raise SemanticErrors.TypeMismatchError().add(parameter, parameter_type, argument, argument_type)

                    elif not parameter_type.symbolic_eq(argument_type, function_scope, scope_manager.current_scope):
                        raise SemanticErrors.TypeMismatchError().add(parameter, parameter_type, argument, argument_type)

                # Mark the overload as a pass.
                pass_overloads.append((function_scope, function_overload))

            except (
                    SemanticErrors.FunctionCallAbstractFunctionError,
                    SemanticErrors.FunctionCallTooManyArgumentsError,
                    SemanticErrors.ArgumentNameInvalidError,
                    SemanticErrors.ArgumentRequiredNameMissingError,
                    SemanticErrors.TypeMismatchError,
                    SemanticErrors.GenericParameterInferredConflictInferredError,
                    SemanticErrors.GenericParameterInferredConflictExplicitError,
                    SemanticErrors.GenericParameterNotInferredError,
                    SemanticErrors.GenericArgumentTooManyError) as e:

                # Mark the overload as a fail.
                fail_overloads.append((function_scope, function_overload, e))
                continue

        # If there are no pass overloads, raise an error.
        if pass_overloads.is_empty():
            failed_signatures_and_errors = fail_overloads.map(lambda f: f[1].print_signature(AstPrinter(), f[0]._ast.name) + f" - {type(f[2]).__name__}").join("\n")
            argument_usage_signature = f"{lhs}({self.function_argument_group.arguments.map(lambda a: a.infer_type(scope_manager, **kwargs)).join(", ")})"
            raise SemanticErrors.FunctionCallNoValidSignaturesError().add(self, failed_signatures_and_errors, argument_usage_signature).scopes(scope_manager.current_scope)

        # If there are multiple pass overloads, raise an error.
        elif pass_overloads.length > 1:
            passed_signatures = pass_overloads.map(lambda f: f[1].print_signature(AstPrinter(), f[0]._ast.name)).join("\n")
            argument_usage_signature = f"{lhs}({self.function_argument_group.arguments.map(lambda a: a.infer_type(scope_manager, **kwargs)).join(", ")})"
            raise SemanticErrors.FunctionCallAmbiguousSignaturesError().add(self, passed_signatures, argument_usage_signature).scopes(scope_manager.current_scope)

        # Set the overload to the only pass overload.
        self._overload = pass_overloads[0]
        if self_param := self._overload[1].function_parameter_group.get_self():
            self.function_argument_group.arguments[0].convention = self_param.convention
        return

    def infer_type(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Todo: Hacky workaround - see why having a function call as a "self" argument doesn't use its "analyse
        #  semantics" as the same object. it calls the analyse_semantics method, but on another instance of the AST -
        #  being copied somewhere, maybe in a code injection.
        if not self._overload:
            self.analyse_semantics(scope_manager, lhs, **kwargs)

        # Return the function's return type.
        return_type = self._overload[1].return_type
        return return_type

    def analyse_semantics(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        if self._overload:
            return

        # Analyse the function and generic arguments, and determine the overload.
        self.function_argument_group.analyse_pre_semantics(scope_manager, **kwargs)
        self.generic_argument_group.analyse_semantics(scope_manager, **kwargs)
        self.determine_overload(scope_manager, lhs, **kwargs)  # Also adds the "self" argument if needed.
        self.function_argument_group.analyse_semantics(scope_manager, target_scope=self._overload[0], target_proto=self._overload[1], is_async=self._is_async, **kwargs)


__all__ = ["PostfixExpressionOperatorFunctionCallAst"]
