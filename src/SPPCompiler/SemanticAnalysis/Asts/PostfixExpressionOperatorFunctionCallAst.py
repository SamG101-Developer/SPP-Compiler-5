from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional, Tuple, TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class PostfixExpressionOperatorFunctionCallAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default=None)
    function_argument_group: Asts.FunctionCallArgumentGroupAst = field(default=None)
    fold_token: Optional[Asts.TokenAst] = field(default=None)

    _overload: Optional[Tuple[Scope, Asts.FunctionPrototypeAst]] = field(default=None, init=False, repr=False)
    _is_async: Optional[Asts.Ast] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.generic_argument_group = self.generic_argument_group or Asts.GenericArgumentGroupAst(pos=self.pos)
        self.function_argument_group = self.function_argument_group or Asts.FunctionCallArgumentGroupAst(pos=self.pos)

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

    def determine_overload(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # 3 types of function calling: function_call(), obj.method_call(), Type::static_method_call(). Determine the
        # function's name and its owner type/namespace.
        # from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope

        # Todo: Change this to detecting FunMov/Mut/Ref superimpositions over the type
        function_owner_type, function_owner_scope, function_name = AstFunctionUtils.get_function_owner_type_and_function_name(sm, lhs)
        if not function_name:
            raise SemanticErrors.FunctionCallOnNoncallableTypeError().add(lhs).scopes(sm.current_scope)

        # Convert the obj.method_call(...args) into Type::method_call(obj, ...args).
        if isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_runtime_access():
            transformed_lhs, transformed_function_call = AstFunctionUtils.convert_method_to_function_form(sm, function_owner_type, function_name, lhs, self)
            transformed_function_call.determine_overload(sm, transformed_lhs, **kwargs)
            self._overload = transformed_function_call._overload
            self.function_argument_group = transformed_function_call.function_argument_group
            return

        # Record the "pass" and "fail" overloads
        all_overloads = AstFunctionUtils.get_all_function_scopes(function_name, function_owner_scope)
        pass_overloads = Seq()
        fail_overloads = Seq()

        for function_scope, function_overload, owner_scope_generic_arguments in all_overloads:
            owner_scope_generic_arguments = owner_scope_generic_arguments.arguments

            # Extract generic/function parameter information from the overload.
            parameters = function_overload.function_parameter_group.params.copy()
            parameter_names = parameters.map_attr("extract_name")
            parameter_names_req = function_overload.function_parameter_group.get_required_params().map_attr("extract_name")
            generic_parameters = function_overload.generic_parameter_group.parameters
            is_variadic = function_overload.function_parameter_group.get_variadic_param() is not None

            # Extract generic/function argument information from this AST.
            arguments = self.function_argument_group.arguments.copy()
            argument_names = arguments.filter_to_type(Asts.FunctionCallArgumentNamedAst).map_attr("name")
            generic_arguments = self.generic_argument_group.arguments.copy()

            # Use a try-except block to catch any errors as a following overload could still be valid.
            try:
                # Can't call an abstract function.
                if function_overload._abstract:
                    raise SemanticErrors.FunctionCallAbstractFunctionError().add(function_overload.name, self).scopes(sm.current_scope)

                # Can't call non-implemented functions (dummy functions).
                if function_overload._non_implemented:
                    ...  # Todo: raise SemanticErrors.FunctionCallNonImplementedMethodError

                # Check if there are too many arguments for the function (non-variadic).
                if arguments.length > parameters.length and not is_variadic:
                    raise SemanticErrors.FunctionCallTooManyArgumentsError().add(self, function_overload.name).scopes(sm.current_scope)

                # Check for any named arguments without a corresponding parameter.
                # Todo: Generic=Void means the associated parameters should be removed.
                if invalid_arguments := argument_names.set_subtract(parameter_names):
                    raise SemanticErrors.ArgumentNameInvalidError().add(parameters[0], "parameter", invalid_arguments[0], "argument").scopes(sm.current_scope)

                # Remove all the used parameters names from the set of parameter names, and name the unnamed arguments.
                AstFunctionUtils.name_function_arguments(arguments, parameters, sm)
                AstFunctionUtils.name_generic_arguments(generic_arguments, generic_parameters, sm)
                argument_names = arguments.map_attr("name")

                # Check if there are too few arguments for the function (by missing names).
                if missing_parameters := parameter_names_req.set_subtract(argument_names):
                    raise SemanticErrors.ArgumentRequiredNameMissingError().add(self, missing_parameters[0], "parameter", "argument")

                # Infer generic arguments and inherit from the function owner block.
                generic_arguments = AstFunctionUtils.infer_generic_arguments(
                    generic_parameters=function_overload.generic_parameter_group.get_required_params(),
                    explicit_generic_arguments=generic_arguments + owner_scope_generic_arguments,
                    infer_source=arguments.map(lambda a: (a.name, a.infer_type(sm, **kwargs))).dict(),
                    infer_target=parameters.map(lambda p: (p.extract_name, p.type)).dict(),
                    sm=sm, owner=lhs,
                    variadic_parameter_identifier=function_overload.function_parameter_group.get_variadic_param().extract_name if is_variadic else None)

                # Create a new overload with the generic arguments applied.
                if generic_arguments:
                    new_overload = copy.deepcopy(function_overload)
                    tm = ScopeManager(sm.global_scope, function_scope)

                    new_overload.generic_parameter_group.parameters = Seq()
                    for p in new_overload.function_parameter_group.params:
                        p.type = p.type.sub_generics(generic_arguments)
                        p.type.analyse_semantics(tm, **kwargs)
                    new_overload.return_type = new_overload.return_type.sub_generics(generic_arguments)
                    new_overload.return_type.analyse_semantics(tm, **kwargs)

                    # Todo: I don't want this here
                    if c := new_overload.return_type.get_convention():
                        raise SemanticErrors.InvalidConventionLocationError().add(
                            c, new_overload.return_type, "function return type").scopes(sm.current_scope)

                    # new_overload.generate_top_level_scopes(tm)
                    # tm.reset(new_overload._scope)

                    parameters = new_overload.function_parameter_group.params.copy()
                    # if new_overload not in function_overload._generic_overrides:
                    #     function_overload._generic_overrides.append(new_overload)
                    #     new_overload.analyse_semantics(tm, **(kwargs | {"no_scope": True}))
                    function_overload = new_overload
                    function_scope = tm.current_scope

                # Type check the arguments against the parameters.
                sorted_arguments = arguments.sort(key=lambda a: parameter_names.index(a.name))
                for argument, parameter in sorted_arguments.zip(parameters):
                    parameter_type = parameter.type
                    argument_type = argument.infer_type(sm, **kwargs)

                    if isinstance(parameter, Asts.FunctionParameterVariadicAst):
                        parameter_type = CommonTypes.Tup(parameter.pos, Seq([parameter_type] * argument_type.type_parts()[0].generic_argument_group.arguments.length))
                        parameter_type.analyse_semantics(sm, **kwargs)

                    if isinstance(parameter, Asts.FunctionParameterSelfAst):
                        argument.convention = parameter.convention
                        argument_type = argument_type.without_generics()

                        if function_overload.function_parameter_group.get_self_param()._arbitrary and not parameter_type.symbolic_eq(argument_type, function_scope, sm.current_scope):
                            raise SemanticErrors.TypeMismatchError().add(parameter, parameter_type, argument, argument_type)

                    elif not parameter_type.symbolic_eq(argument_type, function_scope, sm.current_scope):
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
            argument_usage_signature = f"{lhs}({self.function_argument_group.arguments.map(lambda a: a.infer_type(sm, **kwargs)).join(", ")})"
            raise SemanticErrors.FunctionCallNoValidSignaturesError().add(self, failed_signatures_and_errors, argument_usage_signature).scopes(sm.current_scope)

        # If there are multiple pass overloads, raise an error.
        elif pass_overloads.length > 1:
            passed_signatures = pass_overloads.map(lambda f: f[1].print_signature(AstPrinter(), f[0]._ast.name)).join("\n")
            argument_usage_signature = f"{lhs}({self.function_argument_group.arguments.map(lambda a: a.infer_type(sm, **kwargs)).join(", ")})"
            raise SemanticErrors.FunctionCallAmbiguousSignaturesError().add(self, passed_signatures, argument_usage_signature).scopes(sm.current_scope)

        # Set the overload to the only pass overload.
        self._overload = pass_overloads[0]
        if self_param := self._overload[1].function_parameter_group.get_self_param():
            self.function_argument_group.arguments[0].convention = self_param.convention
        return

    def infer_type(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Todo: Hacky workaround - see why having a function call as a "self" argument doesn't use its "analyse
        #  semantics" as the same object. it calls the analyse_semantics method, but on another instance of the AST -
        #  being copied somewhere, maybe in a code injection.
        if not self._overload:
            self.analyse_semantics(sm, lhs, **kwargs)

        # Return the function's return type.
        return_type = self._overload[1].return_type
        return return_type

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        if self._overload:
            return

        # Analyse the function and generic arguments, and determine the overload.
        self.function_argument_group.analyse_pre_semantics(sm, **kwargs)
        self.generic_argument_group.analyse_semantics(sm, **kwargs)
        self.determine_overload(sm, lhs, **kwargs)  # Also adds the "self" argument if needed.
        self.function_argument_group.analyse_semantics(sm, target_proto=self._overload[1], is_async=self._is_async, **kwargs)

        # Link references created by the function call to the overload.
        if self._overload[1].tok_fun.token_type == SppTokenType.KwCor:
            coro_return_type = self.infer_type(sm, lhs, **kwargs)

            # Find the generator type superimposed over the return type.
            for super_type in sm.current_scope.get_symbol(coro_return_type).scope.sup_types + Seq([coro_return_type]):
                if super_type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATOR, sm.current_scope):
                    coro_return_type = super_type
                    break

            # Immutable reference invalidates all mutable references.
            if type(coro_return_type.type_parts()[-1].generic_argument_group["Yield"].value.get_convention()) is Asts.ConventionRefAst:
                outermost = sm.current_scope.get_variable_symbol_outermost_part(lhs)
                for existing_referred_to, is_mutable in outermost.memory_info.refer_to_asts:
                    if is_mutable:
                        outermost.memory_info.invalidate_referred_borrow(sm, existing_referred_to, self)

                outermost.memory_info.refer_to_asts = Seq([(ast, False) for ast in kwargs.get("assignment", Seq())])

            # Mutable reference invalidates all mutable and immutable references.
            elif type(coro_return_type.type_parts()[-1].generic_argument_group["Yield"].value.get_convention()) is Asts.ConventionMutAst:
                outermost = sm.current_scope.get_variable_symbol_outermost_part(lhs)
                for existing_referred_to, is_mutable in outermost.memory_info.refer_to_asts:
                    outermost.memory_info.invalidate_referred_borrow(sm, existing_referred_to, self)

                outermost.memory_info.refer_to_asts = Seq([(ast, True) for ast in kwargs.get("assignment", Seq())])


__all__ = ["PostfixExpressionOperatorFunctionCallAst"]
