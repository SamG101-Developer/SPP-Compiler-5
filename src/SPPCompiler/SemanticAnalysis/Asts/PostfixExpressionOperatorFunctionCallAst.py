from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Tuple

from ordered_set import OrderedSet

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True)
class PostfixExpressionOperatorFunctionCallAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default=None)
    function_argument_group: Asts.FunctionCallArgumentGroupAst = field(default=None)
    fold_token: Optional[Asts.TokenAst] = field(default=None)

    _overload: Optional[Tuple[Scope, Asts.FunctionPrototypeAst]] = field(default=None, repr=False)
    _is_async: Optional[Asts.Ast] = field(default=None, repr=False)
    _folded_args: Seq[Asts.FunctionCallArgumentAst] = field(default_factory=Seq, repr=False)
    _closure_arg: Optional[Asts.FunctionCallArgumentUnnamedAst] = field(default=None, repr=False)

    def __copy__(self, memodict=None) -> PostfixExpressionOperatorFunctionCallAst:
        return PostfixExpressionOperatorFunctionCallAst(
            self.pos, copy.copy(self.generic_argument_group), copy.copy(self.function_argument_group),
            fold_token=self.fold_token, _is_async=self._is_async, _overload=self._overload, _ctx=self._ctx)

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

    def determine_overload(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, expected_return_type: Asts.TypeAst = None, **kwargs) -> None:
        # Todo: split this function up, might be the worst function in the codebase.

        # 3 types of function calling: function_call(), obj.method_call(), Type::static_method_call(). Determine the
        # function's name and its owner type/namespace.
        function_owner_type, function_owner_scope, function_name = AstFunctionUtils.get_function_owner_type_and_function_name(sm, lhs)

        # Convert the obj.method_call(...args) into Type::method_call(obj, ...args).
        if isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_runtime_access():
            transformed_lhs, transformed_function_call = AstFunctionUtils.convert_method_to_function_form(
                sm, function_owner_type, function_name, lhs, self)
            transformed_function_call.determine_overload(sm, transformed_lhs, expected_return_type=expected_return_type, **kwargs)
            self._overload = transformed_function_call._overload
            self.function_argument_group = transformed_function_call.function_argument_group
            return

        # Record the "pass" and "fail" overloads
        all_overloads = AstFunctionUtils.get_all_function_scopes(function_name, function_owner_scope)
        pass_overloads = []
        fail_overloads = []

        # Create a dummy overload for no-overload identifiers that are function types (lambdas etc).
        is_closure = False
        if not all_overloads and (lhs_type := AstFunctionUtils.is_target_callable(lhs, sm, **kwargs)):
            dummy_proto = AstFunctionUtils.create_callable_prototype(lhs_type)
            all_overloads.append((sm.current_scope, dummy_proto, Asts.GenericArgumentGroupAst()))
            is_closure = True

        for fn_scope, fn_proto, ctx_generic_args in all_overloads:
            ctx_generic_args = ctx_generic_args.arguments

            # Extract generic/function parameter information from the overload.
            parameters         = fn_proto.function_parameter_group.params
            generic_parameters = fn_proto.generic_parameter_group.parameters
            arguments          = self.function_argument_group.arguments.copy()
            generic_arguments  = self.generic_argument_group.arguments.copy()

            # Extract the parameter names and argument names.
            parameter_names     = [p.extract_name for p in fn_proto.function_parameter_group.params]
            parameter_names_req = [p.extract_name for p in fn_proto.function_parameter_group.get_required_params()]
            argument_names      = [a.name for a in arguments if isinstance(a, Asts.FunctionCallArgumentNamedAst)]
            is_variadic_fn      = fn_proto.function_parameter_group.get_variadic_param() is not None

            # Use a try-except block to catch any errors as a following overload could still be valid.
            try:
                # Can't call an abstract function.
                if fn_proto._abstract:
                    raise SemanticErrors.FunctionCallAbstractFunctionError().add(fn_proto.name, self).scopes(sm.current_scope)

                # Can't call non-implemented functions (dummy functions).
                if fn_proto._non_implemented:
                    ...

                # Check if there are too many arguments for the function (non-variadic).
                if len(arguments) > len(parameters) and not is_variadic_fn:
                    raise SemanticErrors.FunctionCallTooManyArgumentsError().add(self, fn_proto.name).scopes(sm.current_scope)

                # Remove all the used parameters names from the set of parameter names, and name the unnamed arguments.
                AstFunctionUtils.name_function_arguments(arguments, parameters, sm)
                AstFunctionUtils.name_generic_arguments(generic_arguments, generic_parameters, sm, fn_proto.name)
                argument_names = [a.name for a in arguments]

                # Infer generic arguments and inherit from the function owner block.
                generic_arguments = AstFunctionUtils.infer_generic_arguments(
                    generic_parameters=fn_proto.generic_parameter_group.parameters,
                    optional_generic_parameters=fn_proto.generic_parameter_group.get_optional_params(),
                    explicit_generic_arguments=generic_arguments + ctx_generic_args,
                    infer_source={a.name: a.infer_type(sm, **kwargs) for a in arguments},
                    infer_target={p.extract_name: p.type for p in parameters},
                    sm=sm, owner=lhs.infer_type(sm, **kwargs),
                    variadic_parameter_identifier=fn_proto.function_parameter_group.get_variadic_param().extract_name if is_variadic_fn else None,
                    **kwargs)

                # For function folding, identify all tuple arguments that have non-tuple parameters.
                if self.fold_token is not None:
                    # Populate the list of arguments to fold.
                    for argument in arguments:
                        if AstTypeUtils.is_type_tuple(argument.infer_type(sm, **kwargs), sm.current_scope):
                            if [p for p in parameters if p.extract_name == argument.name and not AstTypeUtils.is_type_tuple(p.type, sm.current_scope)]:
                                self._folded_args.append(argument)

                    # Tuples being folded must all have the same element types (per tuple).
                    for argument in self._folded_args:
                        first_elem_type = argument.infer_type(sm, **kwargs).type_parts[0].generic_argument_group.arguments[0].value
                        if mismatch := [t.value for t in argument.infer_type(sm, **kwargs).type_parts[0].generic_argument_group.arguments[1:] if not AstTypeUtils.symbolic_eq(t.value, first_elem_type, sm.current_scope, sm.current_scope)]:
                            raise SemanticErrors.FunctionFoldTupleElementTypeMismatchError().add(
                                first_elem_type, mismatch[0]).scopes(sm.current_scope)  # todo: scopes

                    # Ensure all the tuples are of equal length.
                    first_tuple_length = len(self._folded_args[0].infer_type(sm, **kwargs).type_parts[0].generic_argument_group.arguments)
                    for argument in self._folded_args[1:]:
                        tuple_length = len(argument.infer_type(sm, **kwargs).type_parts[0].generic_argument_group.arguments)
                        if tuple_length != first_tuple_length:
                            raise SemanticErrors.FunctionFoldTupleLengthMismatchError().add(
                                self._folded_args[0].value, first_tuple_length, argument.value, tuple_length).scopes(sm.current_scope)

                # Create a new overload with the generic arguments applied.
                if generic_arguments:
                    new_fn_proto = fast_deepcopy(fn_proto)
                    tm = ScopeManager(sm.global_scope, fn_scope, sm.normal_sup_blocks, sm.generic_sup_blocks)

                    new_fn_proto.generic_parameter_group.parameters = []
                    for p in new_fn_proto.function_parameter_group.params.copy():
                        p.type = p.type.substituted_generics(generic_arguments)
                        p.type.analyse_semantics(tm, **kwargs)

                        # Remove a parameter if it is substituted with a "Void" type.
                        # Todo: this should be done outside generic substitution, because what if f(x: Void)
                        #  Maybe make the "if generic_arguments" include "or any(p.type.symbolic_eq(CommonTypesPrecompiled.VOID, tm.current_scope, tm.current_scope) for p in parameters)"
                        if AstTypeUtils.symbolic_eq(p.type, CommonTypesPrecompiled.VOID, tm.current_scope, tm.current_scope):
                            new_fn_proto.function_parameter_group.params.remove(p)

                    new_fn_proto.return_type = new_fn_proto.return_type.substituted_generics(generic_arguments)
                    new_fn_proto.return_type.analyse_semantics(tm, **kwargs)

                    # Todo: I don't want this here
                    if c := new_fn_proto.return_type.convention:
                        raise SemanticErrors.InvalidConventionLocationError().add(
                            c, new_fn_proto.return_type, "function return type").scopes(sm.current_scope)

                    # Extract the new parameter names.
                    parameters          = new_fn_proto.function_parameter_group.params.copy()
                    parameter_names     = [p.extract_name for p in new_fn_proto.function_parameter_group.params]
                    parameter_names_req = [p.extract_name for p in new_fn_proto.function_parameter_group.get_required_params()]

                    # Overwrite the function prototype and scope.
                    fn_proto = new_fn_proto
                    fn_scope = tm.current_scope

                # Check for any named arguments without a corresponding parameter.
                if invalid_arguments := OrderedSet(argument_names) - OrderedSet(parameter_names):
                    raise SemanticErrors.ArgumentNameInvalidError().add(parameters[0], "parameter", invalid_arguments.pop(0), "argument").scopes(sm.current_scope)

                # Check if there are too few arguments for the function (by missing names).
                if missing_parameters := OrderedSet(parameter_names_req) - OrderedSet(argument_names):
                    raise SemanticErrors.ArgumentRequiredNameMissingError().add(self, missing_parameters.pop(0), "parameter", "argument")

                # Type check the arguments against the parameters.
                sorted_arguments = sorted(arguments, key=lambda a: parameter_names.index(a.name))
                for argument, parameter in zip(sorted_arguments, parameters):
                    parameter_type = parameter.type
                    argument_type = argument.infer_type(sm, **kwargs)

                    # Special case for variadic parameters.
                    if isinstance(parameter, Asts.FunctionParameterVariadicAst):
                        parameter_type = CommonTypes.Tup(parameter.pos, [parameter_type] * len(argument_type.type_parts[0].generic_argument_group.arguments))
                        parameter_type.analyse_semantics(sm, **kwargs)

                    # Special case for self parameters.
                    if isinstance(parameter, Asts.FunctionParameterSelfAst):
                        argument.convention = parameter.convention
                        argument_type = argument_type.without_generics

                        if fn_proto.function_parameter_group.get_self_param()._arbitrary and not AstTypeUtils.symbolic_eq(parameter_type, argument_type, fn_scope, sm.current_scope):
                            raise SemanticErrors.TypeMismatchError().add(parameter, parameter_type, argument, argument_type)

                    # Regular parameters (with a folding argument check too).
                    else:
                        if argument in self._folded_args:
                            if not AstTypeUtils.symbolic_eq(parameter_type, argument_type.type_parts[0].generic_argument_group.arguments[0].value, fn_scope, sm.current_scope):
                                raise SemanticErrors.TypeMismatchError().add(parameter, parameter_type, argument, argument_type.type_parts[0].generic_argument_group.arguments[0].value)

                        else:
                            if not AstTypeUtils.symbolic_eq(parameter_type, argument_type, fn_scope, sm.current_scope):
                                raise SemanticErrors.TypeMismatchError().add(parameter, parameter_type, argument, argument_type)

                # Mark the overload as a pass.
                pass_overloads.append((fn_scope, fn_proto))

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
                fail_overloads.append((fn_scope, fn_proto, e))
                continue

        # Perform the return type overload selection separately here, for error reasons.
        return_matches = []
        if expected_return_type:
            for fn_scope, fn_proto in pass_overloads:
                if AstTypeUtils.symbolic_eq(fn_proto.return_type, expected_return_type, fn_scope, sm.current_scope):
                    return_matches.append((fn_scope, fn_proto))
            if len(return_matches) == 1:
                pass_overloads = return_matches

        # If there are no pass overloads, raise an error.
        # Todo: print the convention with "Self" (issue is ".convention" is set at bottom of function after this)
        if not pass_overloads:
            failed_signatures_and_errors = "\n".join([f[1].print_signature(AstPrinter(), f[0]._ast.name if f[0]._ast else "") + f" - {type(f[2]).__name__}" for f in fail_overloads])
            argument_usage_signature = f"{lhs}({", ".join([str(a.infer_type(sm, **kwargs)) if not a._type_from_self else "Self" for a in self.function_argument_group.arguments])})"
            raise SemanticErrors.FunctionCallNoValidSignaturesError().add(self, failed_signatures_and_errors, argument_usage_signature).scopes(sm.current_scope)

        # If there are multiple pass overloads, raise an error.
        elif len(pass_overloads) > 1:
            passed_signatures = "\n".join([f[1].print_signature(AstPrinter(), f[0]._ast.name if f[0]._ast else "") for f in pass_overloads])
            argument_usage_signature = f"{lhs}({", ".join([str(a.infer_type(sm, **kwargs)) if not a._type_from_self else "Self" for a in self.function_argument_group.arguments])})"
            raise SemanticErrors.FunctionCallAmbiguousSignaturesError().add(self, passed_signatures, argument_usage_signature).scopes(sm.current_scope)

        # Special case for closures: apply the convention to the closure name to ensure it is movable or mutable etc.
        if is_closure:
            dummy_self_argument = Asts.FunctionCallArgumentUnnamedAst(pos=lhs.pos, value=lhs)
            if AstTypeUtils.symbolic_eq(lhs_type.without_generics, CommonTypesPrecompiled.EMPTY_FUN_MUT, sm.current_scope, sm.current_scope):
                dummy_self_argument.convention = Asts.ConventionMutAst(pos=lhs.pos)
            elif AstTypeUtils.symbolic_eq(lhs_type.without_generics, CommonTypesPrecompiled.EMPTY_FUN_REF, sm.current_scope, sm.current_scope):
                dummy_self_argument.convention = Asts.ConventionRefAst(pos=lhs.pos)
            self._closure_arg = dummy_self_argument

        # Set the overload to the only pass overload.
        self._overload = pass_overloads[0]
        if self_param := self._overload[1].function_parameter_group.get_self_param():
            self.function_argument_group.arguments[0].convention = self_param.convention
        return

    def infer_type(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Return the function's return type.
        return_type = self._overload[1].return_type

        # If there is a scope present (ie non-lambda), then fully qualify the return type.
        if self._overload[0] is not None:
            return_type = self._overload[0].get_symbol(return_type).fq_name
        return return_type

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        if self._overload:
            return

        # Check if this function call is from a transformed coroutine resume AST.
        inferred_return_type = kwargs.pop("inferred_return_type", None)

        # Analyse the function and generic arguments, and determine the overload.
        self.function_argument_group.analyse_semantics(sm, **kwargs)
        self.generic_argument_group.analyse_semantics(sm, **kwargs)
        self.determine_overload(sm, lhs, expected_return_type=inferred_return_type, **kwargs)

    def check_memory(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Todo: lhs.pos or self.pos for these 2 mock groups?

        # If a fold is taking place, analyse the non-folding arguments again (checks for double moves).
        if self.fold_token is not None and self._folded_args:
            non_folding_arguments = [a for a in self.function_argument_group.arguments if a.value not in [f.value for f in self._folded_args]]
            group = Asts.FunctionCallArgumentGroupAst(pos=lhs.pos, arguments=non_folding_arguments)
            group.check_memory(sm, **kwargs)

        # If a closure is being called, apply memory rules to symbolic target.
        if self._closure_arg:
            group = Asts.FunctionCallArgumentGroupAst(pos=lhs.pos, arguments=[self._closure_arg])
            group.check_memory(sm)

        # Link references created by the function call to the overload. This is only caused by ".res()".
        # if self._overload[1].tok_fun.token_type == SppTokenType.KwCor:
        #     coro_return_type = self.infer_type(sm, lhs, **kwargs)
        #
        #     # Find the generator type superimposed over the return type.
        #     _, yield_type = AstTypeUtils.get_generator_and_yielded_type(
        #         coro_return_type, sm, coro_return_type, "coroutine call")
        #
        #     # Immutable references invalidate all mutable references.
        #     if yield_type.convention.__class__ is Asts.ConventionRefAst:
        #         outermost = sm.current_scope.get_variable_symbol_outermost_part(lhs)
        #         for yielded_borrow, is_mutable in outermost.memory_info.yielded_borrows_linked:
        #             if is_mutable: AstMemoryUtils.invalidate_yielded_borrow(sm, yielded_borrow, self)
        #         outermost.memory_info.yielded_borrows_linked = [(ast, False) for ast in kwargs.get("assignment", [])]
        #
        #     # Mutable references invalidate all mutable and immutable references.
        #     elif yield_type.convention.__class__ is Asts.ConventionMutAst:
        #         outermost = sm.current_scope.get_variable_symbol_outermost_part(lhs)
        #         for yielded_borrow, _ in outermost.memory_info.yielded_borrows_linked:
        #             AstMemoryUtils.invalidate_yielded_borrow(sm, yielded_borrow, self)
        #         outermost.memory_info.yielded_borrows_linked = [(ast, True) for ast in kwargs.get("assignment", [])]

        # Check the argument group, now the old borrows have been invalidated.
        is_coro_resume = kwargs.pop("is_coro_resume", False)
        self.generic_argument_group.check_memory(sm, **kwargs)
        self.function_argument_group.check_memory(
            sm, target_proto=self._overload[1], is_async=self._is_async, is_coro_resume=is_coro_resume, **kwargs)


__all__ = ["PostfixExpressionOperatorFunctionCallAst"]
