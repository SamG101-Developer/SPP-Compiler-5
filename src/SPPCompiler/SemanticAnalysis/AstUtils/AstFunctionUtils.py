from __future__ import annotations

import copy
from collections import defaultdict
from typing import Dict, Optional, TYPE_CHECKING, Tuple, Type

from ordered_set import OrderedSet

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class AstFunctionUtils:
    """!
    This class contains static methods for ASTs that are related to functions. This includes getting function scopes,
    converting method calls to function calls, and inferring generic arguments for functions.
    """

    @staticmethod
    def get_function_owner_type_and_function_name(
            sm: ScopeManager, lhs: Asts.ExpressionAst,
            **kwargs) -> Tuple[Asts.Ast, Optional[Scope], Asts.IdentifierAst]:

        """!
        Get the function owner type, scope and name from an expression AST. This is used to determine information
        related to getting the overloads of a function. The function owner type is the type of the class the method
        belongs to if the callable is a method rather than a free-function. The scope id for the function itself, not
        its owner. This following cases are handled:
            * `object.method()`: runtime access into an object.
            * `Type::method()`: static access into a type.
            * `namespace::function()`: direct access into a namespaced free function.
            * `function()`: direct function call.
            * `<anything else>()`: lambda identifier or invalid function call.

        @param sm The scope manager to access function scopes.
        @param lhs The left-hand side of the function call.

        @return A 3-tuple containing: the function owner type, the function owner scope, and the function name. Given
        the function `MyType::my_function()`:
            * The owner type is "MyType".
            * The scope is the scope of "my_function" (found inside a superimposition scope of "MyType").
            * The name is "my_function".
        """

        # Runtime access into an object: "object.method()".
        if isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_runtime_access():
            function_owner_type = lhs.lhs.infer_type(sm, **kwargs)
            function_name = lhs.op.field
            function_owner_scope = sm.current_scope.get_symbol(function_owner_type).scope

        # Static access into a type: "Type::method()" or "ns::Type::method()".
        elif isinstance(lhs, Asts.PostfixExpressionAst) and isinstance(lhs.lhs, Asts.TypeAst) and lhs.op.is_static_access():
            function_owner_type = lhs.lhs
            function_name = lhs.op.field
            function_owner_scope = sm.current_scope.get_symbol(function_owner_type).scope

        # Direct access into a namespaced free function: "std::console::print("hello")".
        elif isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_static_access():
            function_owner_scope = sm.current_scope.get_namespace_symbol(lhs.lhs).scope
            function_name = lhs.op.field
            function_owner_type = function_owner_scope.get_symbol(function_name).type

        # Direct access into a non-namespaced function: "function()".
        elif isinstance(lhs, Asts.IdentifierAst):
            function_owner_type = None
            function_name = lhs
            function_owner_scope = sm.current_scope.parent_module

        # Non-callable AST.
        else:
            function_owner_type = None
            function_name = lhs
            function_owner_scope = None

        # Return the function owner type and function name.
        return function_owner_type, function_owner_scope, function_name

    @staticmethod
    def convert_method_to_function_form(
            sm: ScopeManager, function_owner_type: Asts.Ast, function_name: Asts.IdentifierAst,
            lhs: Asts.ExpressionAst, fn: Asts.PostfixExpressionOperatorFunctionCallAst,
            **kwargs) -> Tuple[Asts.PostfixExpressionAst, Asts.PostfixExpressionOperatorFunctionCallAst]:

        """
        This conversion function is used to normalize all different function calls, such as converting runtime function
        access into static access functions with self arguments. For example, "t.method(1)" becomes "T::method(t, 1)".
        Note that this will only be called for function calls of the form "t.method()", so the function owner type is
        always valid.

        :param sm: The scope manager to access function scopes.
        :param function_owner_type: The owning type of the function.
        :param function_name: The name of the method on the type.
        :param lhs: The AST representing the left-hand side of the function call (entire expression before "fn").
        :param fn: The AST representing the function call (parenthesis and arguments).
        :return: A 2-tuple containing the new function access, and the new function call. The function access is the
            static accessor, such as "T::method", and the function call is the actual function call, such as "(t, 1)"
            (can be applied to the function access).
        """

        # Create an argument for self, which is the object being called (convention tested later).
        self_argument = Asts.FunctionCallArgumentUnnamedAst(
            pos=lhs.lhs.pos, value=lhs.lhs)
        function_arguments = fn.function_argument_group.arguments.copy()
        function_arguments.insert(0, self_argument)

        # Create the static method access (without the function call and arguments).
        new_function_access = Asts.PostfixExpressionAst(
            pos=lhs.pos, lhs=function_owner_type,
            op=Asts.PostfixExpressionOperatorMemberAccessAst(
                pos=lhs.pos, tok_access=Asts.TokenAst.raw(token_type=SppTokenType.TkDoubleColon), field=function_name))

        # Create the function call with the object as the first argument (represents "self").
        new_function_call = copy.copy(fn)

        # Tell the "self" argument what type it is (keyword "self" inference requires outer AST knowledge).
        new_function_call.function_argument_group.arguments = function_arguments
        new_function_call.function_argument_group.arguments[0]._type_from_self = lhs.lhs.infer_type(sm, **kwargs)
        new_function_call.function_argument_group.arguments[0].value.pos = lhs.lhs.pos

        # Get the overload from the uniform function call.
        return new_function_access, new_function_call

    @staticmethod
    def get_all_function_scopes(
            target_function_name: Asts.IdentifierAst, target_scope: Scope, *, for_override: bool = False)\
            -> Seq[Tuple[Optional[Scope], Asts.FunctionPrototypeAst, Asts.GenericArgumentGroupAst]]:

        """
        Get all the function scopes, and their generic argument groups for a function name in a scope. This is used to
        get all possible overloads for a function, by iterating the valid scopes a function might be found in, and
        matching by name. The generic arguments from the outer scope (ie superimposition) are saved,so they can be
        inherited into the function signature for generic substitution.

        :param target_function_name: The name of the function to get the overloads for.
        :param target_scope: The scope of the class or module that the functions should belong to.
        :param for_override: If the overloads are being checked for an override.
        :return: A list of 3-tuples, containing for each overload, the scope o the function the overload is represented
            by, the function prototype of the overload, and associated generic arguments in the owning context that must
            be inherited into the function signature.
        """

        if not isinstance(target_function_name, Asts.IdentifierAst):
            return []

        # Get the function-type name from the function: "$Func" from "func()".
        target_function_name = target_function_name.to_function_identifier()
        overload_scopes_and_info = []

        # If target scope is None, then the functions are being superimposed over a generic type.
        if target_scope is None:
            return overload_scopes_and_info

        # Check for namespaced (module-level) functions. They will have no "inheritable generics".
        if target_scope.type_symbol is not None and target_scope.type_symbol.__class__ == NamespaceSymbol:
            for ancestor_scope in target_scope.ancestors:

                # Find all the scopes at the module level superimposing a function type over the function.
                for sup_scope in [c for c in ancestor_scope.children if isinstance(c._ast, Asts.SupPrototypeExtensionAst) and c._ast.name == target_function_name]:
                    generics = Asts.GenericArgumentGroupAst()
                    if not for_override:
                        inner_function_scope = sup_scope.children[0]
                    overload_scopes_and_info.append((inner_function_scope, sup_scope._ast.body.members[0], generics))

        # Functions belonging to a type will have inheritable generics from "sup [...] Type { ... }".
        else:

            # If a class scope was provided as the function owner scope, then check all associated super scopes.
            if isinstance(target_scope._ast, Asts.ClassPrototypeAst):
                sup_scopes = target_scope.sup_scopes

            # Otherwise, just use the super scope that was provided, as this isa more "refined" search.
            else:
                sup_scopes = [target_scope]

            # From the super scopes, check each one for "sup $Func ext FunXXX { ... }" superimpositions.
            for sup_scope in sup_scopes:
                for sup_ast in [m for m in sup_scope._ast.body.members if isinstance(m, Asts.SupPrototypeExtensionAst) and m.name == target_function_name]:
                    generics = Asts.GenericArgumentGroupAst(arguments=sup_scope.generics)
                    overload_scopes_and_info.append((sup_scope, sup_ast._scope._ast.body.members[0], generics))

            # When a derived class has overridden a function, the overridden base class function(s) must be removed.
            # This is done by checking for every candidate method, if there is a conflicting method (by signature)
            # closer to the derived class. If there is, then it must be [an overridden / a base] method, and is removed.
            for scope_1, function_1, _ in overload_scopes_and_info.copy():
                for scope_2, function_2, _ in overload_scopes_and_info.copy():
                    if function_1 is not function_2 and target_scope.depth_difference(scope_1) < target_scope.depth_difference(scope_2):
                        conflict = AstFunctionUtils.check_for_conflicting_override(scope_1, scope_2, function_1)
                        if conflict:
                            SequenceUtils.remove_if(overload_scopes_and_info, lambda info, c=conflict: info[1] is c)

            # Adjust the scope in the tuple to the inner function scope, now the superimposition base classes have been
            # removed.
            if not for_override:
                for i, (scope, function, generics) in enumerate(overload_scopes_and_info):
                    overload_scopes_and_info[i] = (scope.children[0], function, generics)

        # Return the overload scopes, and their generic argument groups.
        return overload_scopes_and_info

    @staticmethod
    def check_for_conflicting_overload(
            this_scope: Scope, target_scope: Scope,
            new_func: Asts.FunctionPrototypeAst) -> Optional[Asts.FunctionPrototypeAst]:

        # Get the existing functions callable on this type (belong to this type or any supertype).
        existing = AstFunctionUtils.get_all_function_scopes(new_func._orig, target_scope)
        existing_scopes = [e[0] for e in existing]
        existing_funcs  = [e[1] for e in existing]

        # Check for an overload conflict with all function of the same name.
        for old_scope, old_func in zip(existing_scopes, existing_funcs):

            # Ignore if the method is an identical match on a base class (override) or is the same object.
            if old_func is new_func:
                continue
            if old_func is AstFunctionUtils.check_for_conflicting_override(this_scope, old_scope, new_func, exclude=old_scope):
                continue

            # Ignore if the return types are different.
            if not AstTypeUtils.symbolic_eq(new_func.return_type, old_func.return_type, this_scope, old_scope):
                continue

            # Ignore if there are a different number of required generic parameters.
            if len(new_func.generic_parameter_group.get_type_params()) != len(old_func.generic_parameter_group.get_type_params()) or len(new_func.generic_parameter_group.get_comp_params()) != len(old_func.generic_parameter_group.get_comp_params()):
                continue

            # Get the two parameter lists and create copies to remove duplicate parameters from.
            params_new = copy.copy(new_func.function_parameter_group)
            params_old = copy.copy(old_func.function_parameter_group)

            # Remove all required parameters on the first parameter list off the other parameter list.
            for p, q in zip(new_func.function_parameter_group.params, old_func.function_parameter_group.params):
                if AstTypeUtils.symbolic_eq(p.type, q.type, this_scope, old_scope):
                    SequenceUtils.remove_if(params_new.params, lambda x, p1=p: x.extract_names == p1.extract_names)
                    SequenceUtils.remove_if(params_old.params, lambda x, q1=q: x.extract_names == q1.extract_names)

            # If neither parameter list contains a required parameter, throw an error.
            if Asts.FunctionParameterRequiredAst not in [type(p) for p in params_new.params + params_old.params]:
                return old_func

        return None

    @staticmethod
    def check_for_conflicting_override(
            this_scope: Scope, target_scope: Scope, new_func: Asts.FunctionPrototypeAst, *,
            exclude: Optional[Scope] = None) -> Optional[Asts.FunctionPrototypeAst]:

        # Helper function to get the type of the convention AST applied to the "self" parameter.
        def sc(f: Asts.FunctionPrototypeAst) -> Type[Asts.ConventionAst]:
            return type(f.function_parameter_group.get_self_param().convention) if hs(f) else None

        # Helper function to check if a function has a "self" parameter or not.
        def hs(f: Asts.FunctionPrototypeAst) -> bool:
            return f.function_parameter_group.get_self_param() is not None

        # Get the existing functions callable on this type (belong to this type or any supertype).
        existing = AstFunctionUtils.get_all_function_scopes(new_func._orig, target_scope, for_override=True)
        existing_scopes = [e[0] for e in existing]
        existing_funcs  = [e[1] for e in existing]

        # Check for an overload conflict with all function of the same name.
        for old_scope, old_func in zip(existing_scopes, existing_funcs):

            # Ignore if the method is the same object.
            if old_func is new_func: continue
            if old_scope is exclude: continue

            # Get the two parameter lists and create copies.
            params_new = copy.copy(new_func.function_parameter_group)
            params_old = copy.copy(old_func.function_parameter_group)

            # Check a list of conditions to check for conflicting functions.
            if len(params_new.params) == len(params_old.params):
                if all(p.extract_names == q.extract_names and AstTypeUtils.symbolic_eq(p.type, q.type, this_scope, old_scope, check_variant=False) for p, q in zip(params_new.get_non_self_params(), params_old.get_non_self_params())):
                    if new_func.tok_fun == old_func.tok_fun:
                        if AstTypeUtils.symbolic_eq(new_func.return_type, old_func.return_type, this_scope, old_scope):
                            if hs(new_func) == hs(old_func) and sc(new_func) is sc(old_func):
                                return old_func

        # No conflicting overload found.
        return None

    @staticmethod
    def name_function_arguments(
            arguments: Seq[Asts.FunctionCallArgumentAst], parameters: Seq[Asts.FunctionParameterAst],
            sm: ScopeManager)\
            -> None:

        """!
        Name all function arguments being passed to a function call, by removing used names from the parameter list, and
        then applying the leftover parameter names for the resulting arguments. Special care is taken for the case of a
        variadic parameter, which requires a tuple of the remaining arguments.

        @param arguments The list of arguments being passed to the function.
        @param parameters The list of parameters the function accepts.
        @param sm The scope manager to access the current scope.

        @return None (the arguments are modified in-place).

        @throw SemanticErrors.ArgumentNameInvalidError If an argument name is invalid (doesn't match a parameter name).
        """

        # Get the argument names and parameter names, and check for the existence of a variadic parameter.
        argument_names = [a.name for a in arguments if isinstance(a, Asts.FunctionCallArgumentNamedAst)]
        parameter_names = [parameter.extract_name for parameter in parameters]
        is_variadic = parameters and isinstance(parameters[-1], Asts.FunctionParameterVariadicAst)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := OrderedSet(argument_names) - OrderedSet(parameter_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(
                parameters[0], "parameter", invalid_argument_names.pop(0), "argument").scopes(sm.current_scope)
        parameter_names = OrderedSet(parameter_names) - OrderedSet(argument_names)

        # Name all the unnamed arguments with leftover parameter names.
        for i, unnamed_argument in enumerate([a for a in arguments if isinstance(a, Asts.FunctionCallArgumentUnnamedAst)]):

            parameter_name = parameter_names.pop(0)
            named_argument = Asts.FunctionCallArgumentNamedAst(pos=unnamed_argument.pos, name=parameter_name)

            # The variadic parameter requires a tuple of the remaining arguments. All future arguments are moved into a
            # tuple, and named by the variadic parameter.
            if len(parameter_names) == 0 and is_variadic:
                named_argument.value = Asts.TupleLiteralAst(elems=[a.value for a in arguments[i:]])
                arguments[i] = named_argument
                arguments[:] = arguments[:i + 1]
                break

            # Name the argument by parsing the argument with the next available parameter name from the function
            # signature. Copy specially assigned "self" types if present.
            else:
                named_argument.convention = unnamed_argument.convention
                named_argument._type_from_self = unnamed_argument._type_from_self
                named_argument.value = unnamed_argument.value
                arguments[i] = named_argument

    @staticmethod
    def name_generic_arguments(
            arguments: Seq[Asts.GenericArgumentAst], parameters: Seq[Asts.GenericParameterAst], sm: ScopeManager,
            owner: Asts.TypeAst | Asts.IdentifierAst, is_tuple_owner: bool = False) -> None:

        """
        Name all generic arguments being passed to a function call or a type declaration, by removing used names from
        the parameter list, and then applying the leftover parameter names for the resulting arguments. Special care is
        taken for the case of a variadic parameter, which requires a tuple of the remaining arguments.

        There are many similarities to the function argument naming function, but this function is more complex due to
        the more expressive application of generic arguments; they are not only constrained to function calls, but any
        place a type is defined. As such, further checks are needed to ensure the generic arguments are correctly named.

        :param arguments: The list of generic arguments being passed to the function.
        :param parameters: The list of generic parameters the function accepts.
        :param sm: The scope manager to access the current scope.
        :param owner: The type that owns the generic arguments (the type being instantiated).
        :param is_tuple_owner: If the owner type is a tuple (early return).

        :raise SemanticErrors.ArgumentNameInvalidError: If an argument name is invalid (doesn't match a parameter name).
        :raise SemanticErrors.GenericArgumentTooManyError: If too many generic arguments are passed.
        """

        # Special case for tuples to prevent infinite-recursion.
        if is_tuple_owner: return

        GEN_MAPPING = {
            Asts.GenericTypeParameterRequiredAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterOptionalAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterVariadicAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericCompParameterRequiredAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterOptionalAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterVariadicAst: Asts.GenericCompArgumentNamedAst,
        }

        # Get the argument names and parameter names, and check for the existence of a variadic parameter.
        argument_names = [a.name.name for a in arguments if isinstance(a, Asts.GenericArgumentNamedAst)]
        parameter_names = [p.name.name for p in parameters]
        is_variadic = parameters and isinstance(parameters[-1], Asts.GenericParameterVariadicAst)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := OrderedSet(argument_names) - OrderedSet(parameter_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(
                owner, "owner", invalid_argument_names.pop(0), "generic argument").scopes(sm.current_scope)
        parameter_names = OrderedSet(parameter_names) - OrderedSet(argument_names)

        # Name all the unnamed arguments with leftover parameter names.
        for i, unnamed_argument in enumerate([a for a in arguments if isinstance(a, Asts.GenericArgumentUnnamedAst)]):

            # Raise an error if too many generic arguments are passed.
            if not parameter_names:
                raise SemanticErrors.GenericArgumentTooManyError().add(
                    parameters, owner, unnamed_argument).scopes(sm.current_scope)

            # Name the argument based on the parameter names available.
            parameter_name = parameter_names.pop(0)
            parameter = [p for p in parameters if p.name.name == parameter_name][0]
            ctor: type = GEN_MAPPING[type([p for p in parameters if p.name.name == parameter_name][0])]
            named_argument = ctor(pos=unnamed_argument.pos, name=Asts.TypeSingleAst.from_generic_identifier(parameter_name))

            # The variadic parameter requires a tuple of the remaining arguments.
            if len(parameter_names) == 0 and is_variadic:
                if isinstance(parameter, Asts.GenericTypeParameterVariadicAst):
                    named_argument.value = CommonTypes.Tup(pos=unnamed_argument.pos, inner_types=[a.value for a in arguments[i:]])
                elif isinstance(parameter, Asts.GenericCompParameterVariadicAst):
                    named_argument.value = Asts.TupleLiteralAst(pos=unnamed_argument.pos, elems=[a.value for a in arguments[i:]])

                if isinstance(parameter, Asts.GenericTypeParameterVariadicAst) and not all(isinstance(a, Asts.GenericTypeArgumentAst) for a in arguments[i:]):
                    raise SemanticErrors.GenericArgumentIncorrectVariationError().add(
                        parameter, [a for a in arguments[i:] if not isinstance(a, Asts.GenericTypeArgumentAst)][0], owner).scopes(sm.current_scope)
                elif isinstance(parameter, Asts.GenericCompParameterVariadicAst) and not all(isinstance(a, Asts.GenericCompArgumentAst) for a in arguments[i:]):
                    raise SemanticErrors.GenericArgumentIncorrectVariationError().add(
                        parameter, [a for a in arguments[i:] if not isinstance(a, Asts.GenericCompArgumentAst)][0], owner).scopes(sm.current_scope)

                arguments[i] = named_argument
                arguments[:] = arguments[:i + 1]

                break

            # Set the value of the named argument to the unnamed argument's value.
            else:
                named_argument.value = unnamed_argument.value
                arguments[i] = named_argument

                if isinstance(parameter, Asts.GenericTypeParameterAst) and not isinstance(unnamed_argument, Asts.GenericTypeArgumentAst):
                    raise SemanticErrors.GenericArgumentIncorrectVariationError().add(
                        parameter, unnamed_argument, owner).scopes(sm.current_scope)

                elif isinstance(parameter, Asts.GenericCompParameterAst) and not isinstance(unnamed_argument, Asts.GenericCompArgumentAst):
                    raise SemanticErrors.GenericArgumentIncorrectVariationError().add(
                        parameter, unnamed_argument, owner).scopes(sm.current_scope)

    @staticmethod
    def infer_generic_arguments(
            generic_parameters: Seq[Asts.GenericParameterAst],
            optional_generic_parameters: Seq[Asts.GenericParameterAst],
            explicit_generic_arguments: Seq[Asts.GenericArgumentAst],
            infer_source: Dict[Asts.IdentifierAst, Asts.TypeAst],
            infer_target: Dict[Asts.IdentifierAst, Asts.TypeAst],
            sm: ScopeManager,
            owner: Asts.TypeAst | Asts.ExpressionAst = None,
            variadic_parameter_identifier: Optional[Asts.IdentifierAst] = None,
            is_tuple_owner: bool = False,
            **kwargs)\
            -> Seq[Asts.GenericArgumentAst]:

        """
        This function infers the generic parameters' values based not only on explicit generic arguments, but on other
        values' true types, that were originally declared as generic. For example a generic type T can be inferred from
        an argument's type, whose corresponding parameter is the generic T type. The same goes for object initializer
        arguments and class attributes.

        cls Point[T, U, V, W] {
            x: T
            y: U
            z: V
        }

        let p = Point[W=Bool](x=1, y="hello", z=False)

        * generic_parameter: [T, U, V, W]
        * explicit_generic_arguments: [W=Bool]
        * infer_source: {x: BigInt, y: Str, z: Bool}
        * infer_target: {x: T, y: U, z: V}

        Todo: variadic generic parameters combined with variadic function parameters.
         - Needs to append the type to the tuple rather than set it as a value and then check for matches.

        :param generic_parameters: The generic parameters that need the values assigned via inference.
        :param optional_generic_parameters: The defaults to fill missing generic arguments with.
        :param explicit_generic_arguments: Any explicit generic arguments that have been given with [] syntax.
        :param infer_source: Function or object initializer arguments.
        :param infer_target: Function parameters or attributes (that have generic type annotations).
        :param sm: The scope manager to access the current scope.
        :param owner: An optional "owner" type (exclusive to types rather than function calls).
        :param variadic_parameter_identifier: An optional parameter name that is known to be variadic.
        :param is_tuple_owner: If the owner is a tuple type, which prevents creating Tup[Tup[...]] infinitely.
        :return: A list of generic arguments with inferred values.

        :raise SemanticErrors.GenericParameterInferredConflictInferredError: If the inferred generic arguments conflict.
        :raise SemanticErrors.GenericParameterInferredConflictExplicitError: If the inferred generic arguments conflict
            with explicit generic arguments.
        :raise SemanticErrors.GenericParameterNotInferredError: If a generic parameter has not been inferred.
        """

        # Special case for tuples to prevent infinite-recursion.
        if is_tuple_owner: return explicit_generic_arguments

        # If there are no generic parameters then skip any inference checks.
        if not generic_parameters: return explicit_generic_arguments

        GEN_MAPPING = {
            Asts.GenericTypeParameterRequiredAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterOptionalAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterVariadicAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericCompParameterRequiredAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterOptionalAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterVariadicAst: Asts.GenericCompArgumentNamedAst,
        }

        # print("-" * 100)
        # print("generic_parameters", [str(p) for p in generic_parameters])
        # print("optional_generic_parameters", [str(p) for p in optional_generic_parameters])
        # print("explicit_generic_arguments", [str(e) for e in explicit_generic_arguments])
        # print("infer_source", Seq([f"{k}={v}" for k, v in infer_source.items()]))
        # print("infer_target", Seq([f"{k}={v}" for k, v in infer_target.items()]))
        # print("owner", owner, sm.current_scope)

        generic_parameter_names = [p.name for p in generic_parameters]

        # The inferred generics map is: {TypeAst: [TypeAst]}. This represents all the types that have been inferred per
        # generic parameter. For example, two "T" parameters with "Str" arguments would be: {"T": [Str, Str]}. This is
        # used to check for conflicts and to ensure each generic parameter has been inferred.
        inferred_generic_arguments = defaultdict(list)

        # Add the explicit generic arguments to the inferred generic arguments. These are inserted here, because the
        # inferred generic arguments map requires all instances of arguments to be present.
        for explicit_generic_argument in explicit_generic_arguments:
            inferred_generic_arguments[explicit_generic_argument.name].append(explicit_generic_argument.value)

        # Infer the generic arguments from the source to the target. This maps arguments to parameters, or object
        # arguments to attributes etc.
        for generic_parameter_name in generic_parameter_names:

            # Check every generic argument on the infer target (function parameters or attributes; these are the generic
            # arguments that are known to be inferrable).
            for infer_target_name, infer_target_type in infer_target.items():
                inferred_generic_argument = None

                # Check for direct match (a: T vs a: BigInt).
                if infer_target_type == generic_parameter_name and infer_target_name in infer_source:
                    inferred_generic_argument = infer_source[infer_target_name]

                # Check for inner match (a: Vec[T] vs a: Vec[BigInt]).
                elif infer_target_name in infer_source:
                    inferred_generic_argument = infer_source[infer_target_name].get_corresponding_generic(infer_target_type, generic_parameter_name)

                # Handle the match if it exists.
                if inferred_generic_argument:
                    inferred_generic_arguments[generic_parameter_name].append(inferred_generic_argument)

                # Handle the variadic parameter if it exists.
                if variadic_parameter_identifier and infer_target_name == variadic_parameter_identifier:
                    inferred_generic_arguments[generic_parameter_name][-1] = inferred_generic_arguments[generic_parameter_name][-1].type_parts[0].generic_argument_group.arguments[0].value

        # Add any default generic arguments in that were missing.
        if sm.current_scope.get_symbol(owner):
            tm = ScopeManager(sm.global_scope, sm.current_scope.get_symbol(owner).scope)
            for optional_generic_parameter in optional_generic_parameters:
                if optional_generic_parameter.name not in inferred_generic_arguments:
                    default = optional_generic_parameter.default
                    if isinstance(owner, Asts.TypeAst) and tm.current_scope.get_symbol(default):
                        default = tm.current_scope.get_symbol(default).fq_name
                    inferred_generic_arguments[optional_generic_parameter.name].append(default)

        # Check each generic argument name only has one unique inferred type. This is to prevent conflicts for a generic
        # type. For example, "T" can't be inferred as a "Str" and then a "BigInt". All instances must match the first
        # inference, in this case "Str".
        for inferred_generic_argument_name, inferred_generic_argument_value in inferred_generic_arguments.items():
            if mismatch := [t for t in inferred_generic_argument_value[1:] if not AstTypeUtils.symbolic_eq(t, inferred_generic_argument_value[0], sm.current_scope, sm.current_scope)]:
                raise SemanticErrors.GenericParameterInferredConflictInferredError().add(
                    inferred_generic_argument_name, inferred_generic_argument_value[0], mismatch[0]).scopes(sm.current_scope)

        # Check inferred generics aren't passed explicitly. This check is present to remove redundant explicit generic
        # arguments in the code. Whilst it wouldn't have an effect on the compilation, it would be a code smell.
        for inferred_generic_argument_name, inferred_generic_argument_value in inferred_generic_arguments.items():
            if inferred_generic_argument_name in explicit_generic_arguments and len(inferred_generic_argument_value) > 1:
                raise SemanticErrors.GenericParameterInferredConflictExplicitError().add(
                    inferred_generic_argument_name, inferred_generic_argument_value[0], explicit_generic_arguments[inferred_generic_argument_name]).scopes(sm.current_scope)

        # Check all the generic parameters have been inferred. Any un-inferred generic argument causes an error, because
        # the types must be known when the function is called, or the type is defined.
        for generic_parameter_name in generic_parameter_names:
            if generic_parameter_name not in inferred_generic_arguments:
                raise SemanticErrors.GenericParameterNotInferredError().add(
                    generic_parameter_name, owner).scopes(sm.current_scope)  # , sm.current_scope.get_symbol(owner).scope.parent_module)

        # At this point, each inferred generic argument has been checked for conflicts, so it is safe to assume the
        # first type mapping per argument can be used. Extract these types into a new dictionary.
        formatted_generic_arguments = {}
        for generic_parameter_name, [generic_parameter_value, *_] in inferred_generic_arguments.copy().items():
            formatted_generic_arguments[generic_parameter_name] = generic_parameter_value

        # Cross apply all generics. This allows generics from previous arguments to be used in future arguments. For
        # example, Cls[T, Vec[T]] when T.
        for generic_parameter_name, generic_parameter_value in formatted_generic_arguments.copy().items():
            if isinstance(generic_parameter_value, Asts.TypeAst):
                args_excluding_this_one = formatted_generic_arguments.copy()
                del args_excluding_this_one[generic_parameter_name]

                formatted_generic_arguments[generic_parameter_name] = generic_parameter_value.substituted_generics(
                    Asts.GenericArgumentGroupAst.from_dict(args_excluding_this_one).arguments)

        # Create the inferred generic arguments, by passing the generic arguments map into the parser, to produce a
        # GenericXXXArgumentASTs. Todo: pos_adjust?
        pos_adjust = owner.pos if owner else 0
        final_args = []
        for k, v in formatted_generic_arguments.items():
            ctor: type = GEN_MAPPING[type([p for p in generic_parameters if p.name == k][0])]
            value = Asts.IdentifierAst.from_type(v) if isinstance(v, Asts.TypeAst) and ctor is Asts.GenericCompArgumentNamedAst else v
            final_args.append(ctor(pos=pos_adjust, name=k, value=value))

        # Re-order the arguments to match the parameter order.
        final_args.sort(key=lambda arg: generic_parameter_names.index(arg.name))

        # For the "comp" args, type-check them. Don't do this before the semantic analysis stage (types haven't been
        # setup correctly yet, and will be analysed anyway later).
        if kwargs["stage"] > 5:
            for comp_arg, comp_param in zip(final_args, generic_parameters):
                if isinstance(comp_arg, Asts.GenericCompArgumentNamedAst):
                    a_type = comp_arg.value.infer_type(sm, **kwargs)
                    p_type = comp_param.type.substituted_generics(final_args)

                    # For a variadic comp argument, check every element of the args tuple.
                    if isinstance(comp_param, Asts.GenericCompParameterVariadicAst):
                        for a_type_inner in a_type.type_parts[0].generic_argument_group.arguments:
                            if not AstTypeUtils.symbolic_eq(p_type, a_type_inner.value, sm.current_scope.get_symbol(owner).scope, sm.current_scope):
                                raise SemanticErrors.TypeMismatchError().add(
                                    comp_param, p_type, comp_arg, a_type_inner.value).scopes(sm.current_scope)

                    # Otherwise, just check the argument type against the parameter type.
                    elif not AstTypeUtils.symbolic_eq(p_type, a_type, sm.current_scope.get_symbol(owner).scope, sm.current_scope):
                        raise SemanticErrors.TypeMismatchError().add(
                            comp_param, p_type, comp_arg, a_type).scopes(sm.current_scope)

        # Finally, re-order the arguments to match the parameter order.
        return final_args

    @staticmethod
    def is_target_callable(expr: Asts.ExpressionAst, sm: ScopeManager, **kwargs) -> Optional[Asts.TypeAst]:
        """
        This function checks that, given provided information during function overload resolution, if the expression
        provided represents a callable type or not. The check is only executed if there are no provided overloads, and
        if the type is functional (one of the FunXXX types, then the type is returned).
        :param expr: The expression to check.
        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The function type is the expression is a function type, otherwise None.
        """

        # Infer the expression's type, and compare it against the known function types.
        expr_type = expr.infer_type(sm, **kwargs)
        is_type_functional = AstTypeUtils.is_type_functional(expr_type, sm.current_scope)
        return expr_type if is_type_functional else None

    @staticmethod
    def create_callable_prototype(expr_type: Asts.TypeAst) -> Asts.FunctionPrototypeAst:
        """
        This function generates a dummy prototype for a callable type. This is for when a callable variable exists;
        there is no "function prototype" to point to, because any function could have been assigned to it, given the
        signature matches, so a temporary dummy prototype is created.
        :param expr_type: The type of the callable variable.
        :return: The dummy prototype for the callable variable.
        """

        # Extract the parameter and return types from the expression type.
        dummy_params_types = [t.value for t in expr_type.type_parts[-1].generic_argument_group["Args"].value.type_parts[-1].generic_argument_group.arguments]
        dummy_return_type = expr_type.type_parts[-1].generic_argument_group["Out"].value

        # Create a function prototype based off of the parameter and return types.
        dummy_params = Asts.FunctionParameterGroupAst(params=[Asts.FunctionParameterRequiredAst(type=t) for t in dummy_params_types])
        dummy_overload = Asts.FunctionPrototypeAst(function_parameter_group=dummy_params, return_type=dummy_return_type)
        return dummy_overload
