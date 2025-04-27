from __future__ import annotations

import copy
import operator
from collections import defaultdict
from typing import Dict, Optional, Tuple, TYPE_CHECKING, Type

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled, CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class AstFunctionUtils:
    """!
    This class contains static methods for ASTs that are related to functions. This includes getting function scopes,
    converting method calls to function calls, and inferring generic arguments for functions.
    """

    @staticmethod
    def get_function_owner_type_and_function_name(sm: ScopeManager, lhs: Asts.ExpressionAst)\
            -> Tuple[Asts.Ast, Optional[Scope], Asts.IdentifierAst]:

        """!
        Get the function owner type, scope and name from an expression AST. This is used to determine information
        related to getting the overloads of a function. The function owner type is the type of the class the method
        belongs to if the callable is a method rather than a free-function. The scope id for the function itself, not
        its owner. This following cases are handled:
            * `generator.res()`: keyword function on generators maps to `.next()`.
            * `object.method()`: runtime access into an object.
            * `Type::method()`: static access into a type.
            * `function()`: direct function call.
            * `<anything else>()`: invalid function call.

        @param sm The scope manager to access function scopes.
        @param lhs The left-hand side of the function call.

        @return A 3-tuple containing: the function owner type, the function owner scope, and the function name. Given
        the function `MyType::my_function()`:
            * The owner type is "MyType".
            * The scope is the scope of "my_function" (found inside a superimposition scope of "MyType").
            * The name is "my_function".
        """

        lhs_type = lhs.infer_type(sm)

        # Runtime access into an object: "object.method()".
        if isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_runtime_access():
            function_owner_type = lhs.lhs.infer_type(sm)
            function_name = lhs.op.field
            function_owner_scope = sm.current_scope.get_symbol(function_owner_type).scope

        # Static access into a type: "Type::method()".
        elif isinstance(lhs, Asts.PostfixExpressionAst) and isinstance(lhs.lhs, Asts.TypeAst) and lhs.op.is_static_access():
            function_owner_type = lhs.lhs
            function_name = lhs.op.field
            function_owner_scope = sm.current_scope.get_symbol(function_owner_type).scope

        # Direct access into a namespaced free function: "std::console::print("hello")".
        elif isinstance(lhs, Asts.PostfixExpressionAst) and isinstance(lhs.lhs.op.field, Asts.IdentifierAst) and lhs.op.is_static_access():
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
            lhs: Asts.ExpressionAst, fn: Asts.PostfixExpressionOperatorFunctionCallAst)\
            -> Tuple[Asts.PostfixExpressionAst, Asts.PostfixExpressionOperatorFunctionCallAst]:

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
        new_function_call.function_argument_group.arguments[0]._type_from_self = lhs.lhs.infer_type(sm)
        new_function_call.function_argument_group.arguments[0].value.pos = lhs.lhs.pos

        # Get the overload from the uniform function call.
        return new_function_access, new_function_call

    @staticmethod
    def get_all_function_scopes(
            function_name: Asts.IdentifierAst, function_owner_scope: Scope)\
            -> Seq[Tuple[Optional[Scope], Asts.FunctionPrototypeAst, Asts.GenericArgumentGroupAst]]:

        """
        Get all the function scopes, and their generic argument groups for a function name in a scope. This is used to
        get all possible overloads for a function, by iterating the valid scopes a function might be found in, and
        matching by name. The generic arguments from the outer scope (ie superimposition) are saved,so they can be
        inherited into the function signature for generic substitution.

        :param function_name: The name of the function to get the overloads for.
        :param function_owner_scope: The scope of the class or module that the function belongs to.
        :return: A list of 3-tuples, containing for each overload, the scope o the function the overload is represented
            by, the function prototype of the overload, and associated generic arguments in the owning context that must
            be inherited into the function signature.
        """

        # Get the function-type name from teh function: "$Func" from "func()".
        function_name = function_name.to_function_identifier()
        overload_scopes_and_info = Seq()

        # Functions at the module level will have no inheritable generics (no enclosing superimposition). They can
        # appear in the current module or any parent module as they are all parent modules' functions are directly
        # accessible from a module.
        if isinstance(function_owner_scope.name, Asts.IdentifierAst):
            for ancestor_scope in function_owner_scope.ancestors:

                # Find all the scopes at the module level that superimpose a function type over the function:
                # "sup $Func ext FunXXX { ... }". Note that these superimpositions should always be extending FunXXX
                # types, because "fun func()" is preprocessed into "sup $Func ext FunRef[...] { ... }".
                for sup_scope in ancestor_scope.children.filter(lambda c: isinstance(c._ast, Asts.SupPrototypeExtensionAst) and c._ast.name == function_name):
                    generics = Asts.GenericArgumentGroupAst()
                    overload_scopes_and_info.append((ancestor_scope, sup_scope._ast.body.members[0], generics))

        # Functions belonging to a type will have inheritable generics from "sup [...] Type { ... }". Note that either a
        # class for the type of the function's owner ("cls Type"), or a specific superimposition ("sup Type ..."), can
        # be provided as the function scope's owner. If a class is provided, then super-scopes are retrieved from it.
        # Otherwise, the superimposition's scope is used directly.
        else:
            if isinstance(function_owner_scope._ast, Asts.ClassPrototypeAst):
                sup_scopes = function_owner_scope.sup_scopes
            else:
                sup_scopes = Seq([function_owner_scope])

            # From the super scopes, check each one for "sup $Func ext FunXXX { ... }" superimpositions. These, as seen
            # in the module analysis version, should also only contain FunXXX types. The only addition is grabbing the
            # generics from the superimposition.
            for sup_scope in sup_scopes:
                for sup_ast in sup_scope._ast.body.members.filter_to_type(Asts.SupPrototypeExtensionAst).filter(lambda m: m.name == function_name):
                    generics = AstTypeUtils.get_generics_in_scope(sup_scope)
                    overload_scopes_and_info.append((sup_scope, sup_ast._scope._ast.body.members[0], generics))

            # When a derived class has overridden a function, the overridden base class function(s) must be removed.
            # This is done by checking for every candidate method, if there is a conflicting method (by signature)
            # closer to the derived class. If there is, then it must be an overridden / a base method, and is removed.
            for scope_1, function_1, _ in overload_scopes_and_info.copy():
                for scope_2, function_2, _ in overload_scopes_and_info.copy():
                    if function_1 is not function_2 and function_owner_scope.depth_difference(scope_1) < function_owner_scope.depth_difference(scope_2):
                        conflict = AstFunctionUtils.check_for_conflicting_override(scope_1, scope_2, function_1)
                        if conflict:
                            overload_scopes_and_info.remove_if(lambda info: info[1] is conflict)

        # Return the overload scopes, and their generic argument groups.
        return overload_scopes_and_info

    @staticmethod
    def check_for_conflicting_overload(
            this_scope: Scope, target_scope: Scope,
            new_func: Asts.FunctionPrototypeAst) -> Optional[Asts.FunctionPrototypeAst]:

        # Get the existing functions callable on this type (belong to this type or any supertype).
        existing = AstFunctionUtils.get_all_function_scopes(new_func._orig, target_scope)
        existing_scopes = existing.map(operator.itemgetter(0))
        existing_funcs = existing.map(operator.itemgetter(1))

        # Check for an overload conflict with all function of the same name.
        for old_scope, old_func in existing_scopes.zip(existing_funcs):
            # Ignore if the method is an identical match on a base class (override) or is the same object.
            if old_func is new_func:
                continue
            if old_func is AstFunctionUtils.check_for_conflicting_override(this_scope, old_scope, new_func, exclude=old_scope):
                continue

            # Get the two parameter lists and create copies to remove duplicate parameters from.
            params_new = copy.copy(new_func.function_parameter_group)
            params_old = copy.copy(old_func.function_parameter_group)

            # Remove all required parameters on the first parameter list off the other parameter list.
            for p, q in new_func.function_parameter_group.params.zip(old_func.function_parameter_group.params):
                if p.type.symbolic_eq(q.type, this_scope, old_scope):
                    params_new.params.remove_if(lambda x: x.extract_names == p.extract_names)
                    params_old.params.remove_if(lambda x: x.extract_names == q.extract_names)

            # If neither parameter list contains a required parameter, throw an error.
            if not (params_new.params + params_old.params).map(type).contains(Asts.FunctionParameterRequiredAst):
                return old_func

        return None

    @staticmethod
    def check_for_conflicting_override(
            this_scope: Scope, target_scope: Scope, new_func: Asts.FunctionPrototypeAst, *,
            exclude: Optional[Scope] = None) -> Optional[Asts.FunctionPrototypeAst]:

        exclude = exclude or Seq()

        # Helper function to get the type of the convention AST applied to the "self" parameter.
        def sc(f: Asts.FunctionPrototypeAst) -> Type[Asts.ConventionAst]:
            return type(f.function_parameter_group.get_self_param().convention) if hs(f) else None

        # Helper function to check if a function has a "self" parameter or not.
        def hs(f: Asts.FunctionPrototypeAst) -> bool:
            return f.function_parameter_group.get_self_param() is not None

        # Get the existing functions callable on this type (belong to this type or any supertype).
        existing = AstFunctionUtils.get_all_function_scopes(new_func._orig, target_scope)
        existing_scopes = existing.map(operator.itemgetter(0))
        existing_funcs = existing.map(operator.itemgetter(1))

        # Check for an overload conflict with all function of the same name.
        for old_scope, old_func in existing_scopes.zip(existing_funcs):

            # Ignore if the method is the same object.
            if old_func is new_func: continue
            if old_scope is exclude: continue

            # Get the two parameter lists and create copies.
            params_new = copy.copy(new_func.function_parameter_group)
            params_old = copy.copy(old_func.function_parameter_group)

            # Check a list of conditions to check for conflicting functions.
            if params_new.params.length == params_old.params.length:
                if all(p.extract_names == q.extract_names and p.type.symbolic_eq(q.type, this_scope, old_scope, check_variant=False) for p, q in zip(params_new.get_non_self_params(), params_old.get_non_self_params())):
                    if new_func.tok_fun == old_func.tok_fun:
                        if new_func.return_type.symbolic_eq(old_func.return_type, this_scope, old_scope):
                            if hs(new_func) == hs(old_func) and sc(new_func) is sc(old_func):
                                return old_func

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
        argument_names = arguments.filter_to_type(Asts.FunctionCallArgumentNamedAst).map_attr("name")
        parameter_names = parameters.map_attr("extract_name")
        is_variadic = parameters and isinstance(parameters[-1], Asts.FunctionParameterVariadicAst)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := argument_names.set_subtract(parameter_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(
                parameters[0], "parameter", invalid_argument_names[0], "argument").scopes(sm.current_scope)
        parameter_names = parameter_names.set_subtract(argument_names)

        # Name all the unnamed arguments with leftover parameter names.
        for i, unnamed_argument in arguments.filter_to_type(Asts.FunctionCallArgumentUnnamedAst).enumerate():

            # The variadic parameter requires a tuple of the remaining arguments. All future arguments are moved into a
            # tuple, and named by the variadic parameter.
            if parameter_names.length == 1 and is_variadic:
                named_argument = Asts.FunctionCallArgumentNamedAst(pos=unnamed_argument.pos, name=parameter_names.pop(0), value=Asts.TupleLiteralAst(elems=arguments[i:].map_attr("value"), pos=unnamed_argument.pos))
                arguments.replace(unnamed_argument, named_argument, 1)
                arguments.pop_n(-1, arguments.length - i - 1)
                break

            # Name the argument by parsing the argument with the next available parameter name from the function
            # signature. Copy specially assigned "self" types if present.
            else:
                parameter_name = parameter_names.pop(0)
                named_argument = Asts.FunctionCallArgumentNamedAst(
                    name=parameter_name,
                    convention=unnamed_argument.convention,
                    value=unnamed_argument.value,
                    _type_from_self=unnamed_argument._type_from_self)
                arguments.replace(unnamed_argument, named_argument, 1)

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
        :return: None (the generic arguments are modified in-place).

        :raise SemanticErrors.ArgumentNameInvalidError: If an argument name is invalid (doesn't match a parameter name).
        :raise SemanticErrors.GenericArgumentTooManyError: If too many generic arguments are passed.
        """

        GEN_MAPPING = {
            Asts.GenericTypeParameterRequiredAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterOptionalAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterVariadicAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericCompParameterRequiredAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterOptionalAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterVariadicAst: Asts.GenericCompArgumentNamedAst,
        }

        # Special case for tuples to prevent infinite-recursion.
        if is_tuple_owner: return

        # Get the argument names and parameter names, and check for the existence of a variadic parameter.
        argument_names = arguments.filter_to_type(*Asts.GenericArgumentNamedAst.__args__).map(lambda a: a.name.name)
        parameter_names = parameters.map(lambda p: p.name.name)
        is_variadic = parameters and isinstance(parameters[-1], Asts.GenericParameterVariadicAst.__args__)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := argument_names.set_subtract(parameter_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(
                parameters.at(0), "generic parameter", invalid_argument_names[0], "generic argument").scopes(sm.current_scope)
        parameter_names = parameter_names.set_subtract(argument_names)

        # Name all the unnamed arguments with leftover parameter names.
        # Todo: does this work with comp and type unnamed args?
        for i, unnamed_argument in arguments.filter_to_type(*Asts.GenericArgumentUnnamedAst.__args__).enumerate():

            # The variadic parameter requires a tuple of the remaining arguments. All future arguments are moved into a
            # tuple, and named by the variadic parameter.
            if parameter_names.length == 1 and is_variadic:
                parameter_name = parameter_names.pop(0)
                ctor: type = GEN_MAPPING[type(parameters.find(lambda g: g.name.name == parameter_name))]
                named_argument = ctor(pos=unnamed_argument.pos, name=Asts.TypeSingleAst.from_generic_identifier(parameter_name), value=CommonTypes.Tup2(pos=unnamed_argument.pos, inner_types=arguments[i:].map_attr("value")))
                arguments.replace(unnamed_argument, named_argument, 1)
                arguments.pop_n(-1, arguments.length - i - 1)
                break

            # Name the argument by parsing the argument with the next available parameter name from the type definition
            # (class prototype). If too many generic arguments have been given, raise an error. This test is done here
            # due to many different places requiring it. It is not seen in the function naming function, because it is
            # handled in the single caller of that function; analysing function call ASTs.
            else:
                try:
                    parameter_name = parameter_names.pop_with_error(0)
                    ctor: type = GEN_MAPPING[type(parameters.find(lambda g: g.name.name == parameter_name))]
                    named_argument = ctor(pos=unnamed_argument.pos, name=Asts.TypeSingleAst.from_generic_identifier(parameter_name), value=unnamed_argument.value)
                    arguments.replace(unnamed_argument, named_argument, 1)

                # If too many generic arguments have been given, raise an error.
                except IndexError:
                    raise SemanticErrors.GenericArgumentTooManyError().add(
                        parameters, owner, unnamed_argument).scopes(sm.current_scope)

        # For any default generic values, override the default "T=T" with "T=Str" etc.
        # for parameter in parameters.filter_to_type(Asts.GenericParameterOptionalAst):
        #     arguments.find(lambda a: a.name == parameter.name).value = parameter.default

    @staticmethod
    def infer_generic_arguments(
            generic_parameters: Seq[Asts.GenericParameterAst],
            optional_generic_parameters: Seq[Asts.GenericParameterAst],
            explicit_generic_arguments: Seq[Asts.GenericArgumentAst],
            infer_source: Dict[Asts.IdentifierAst, Asts.TypeAst],
            infer_target: Dict[Asts.IdentifierAst, Asts.TypeAst],
            sm: ScopeManager,
            owner: Asts.TypeAst | Asts.ExpressionAst = None,
            variadic_parameter_identifier: Optional[Asts.IdentifierAst] = None)\
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

        :param generic_parameters: The generic parameters that need the values assigned via inference.
        :param optional_generic_parameters: The defaults to fill missing generic arguments with.
        :param explicit_generic_arguments: Any explicit generic arguments that have been given with [] syntax.
        :param infer_source: Function or object initializer arguments.
        :param infer_target: Function parameters or attributes (that have generic type annotations).
        :param sm: The scope manager to access the current scope.
        :param owner: An optional "owner" type (exclusive to types rather than function calls).
        :param variadic_parameter_identifier: An optional parameter name that is known to be variadic.
        :return: A list of generic arguments with inferred values.

        :raise SemanticErrors.GenericParameterInferredConflictInferredError: If the inferred generic arguments conflict.
        :raise SemanticErrors.GenericParameterInferredConflictExplicitError: If the inferred generic arguments conflict
            with explicit generic arguments.
        :raise SemanticErrors.GenericParameterNotInferredError: If a generic parameter has not been inferred.
        """

        GEN_MAPPING = {
            Asts.GenericTypeParameterRequiredAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterOptionalAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericTypeParameterVariadicAst: Asts.GenericTypeArgumentNamedAst,
            Asts.GenericCompParameterRequiredAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterOptionalAst: Asts.GenericCompArgumentNamedAst,
            Asts.GenericCompParameterVariadicAst: Asts.GenericCompArgumentNamedAst,
        }

        # print("-" * 100)
        # print("generic_parameters", generic_parameters)
        # print("optional_generic_parameters", optional_generic_parameters)
        # print("explicit_generic_arguments", explicit_generic_arguments)
        # print("infer_source", Seq([f"{k}={v}" for k, v in infer_source.items()]))
        # print("infer_target", Seq([f"{k}={v}" for k, v in infer_target.items()]))
        # print("owner", owner, sm.current_scope)

        # Special case for tuples to prevent infinite-recursion.
        if isinstance(owner, Asts.TypeAst) and sm.current_scope.get_symbol(owner) and owner.symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, sm.current_scope):
            return explicit_generic_arguments

        # If there are no generic parameters then skip any inference checks.
        if generic_parameters.is_empty():
            return explicit_generic_arguments

        # The inferred generics map is: {TypeAst: [TypeAst]}. This represents all the types that have been inferred per
        # generic parameter. For example, two "T" parameters with "Str" arguments would be: {"T": [Str, Str]}. This is
        # used to check for conflicts and to ensure each generic parameter has been inferred.
        inferred_generic_arguments = defaultdict(Seq)

        # Add the explicit generic arguments to the inferred generic arguments. These are inserted here, because the
        # inferred generic arguments map requires all instances of arguments to be present.
        for explicit_generic_argument in explicit_generic_arguments:
            inferred_generic_arguments[explicit_generic_argument.name].append(explicit_generic_argument.value)

        # Infer the generic arguments from the source to the target. This maps arguments to parameters, or object
        # arguments to attributes etc.
        for generic_parameter_name in generic_parameters.map_attr("name"):

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
                    inferred_generic_arguments[generic_parameter_name][-1] = inferred_generic_arguments[generic_parameter_name][-1].type_parts()[0].generic_argument_group.arguments[0].value

        # Add any default generic arguments in that were missing.
        for optional_generic_parameter in optional_generic_parameters:
            if optional_generic_parameter.name not in inferred_generic_arguments:
                default = optional_generic_parameter.default
                if isinstance(owner, Asts.TypeAst):
                    default = sm.current_scope.get_symbol(owner).scope.get_symbol(default).fq_name
                inferred_generic_arguments[optional_generic_parameter.name].append(default)

        # Check each generic argument name only has one unique inferred type. This is to prevent conflicts for a generic
        # type. For example, "T" can't be inferred as a "Str" and then a "BigInt". All instances must match the first
        # inference, in this case "Str".
        for inferred_generic_argument_name, inferred_generic_argument_value in inferred_generic_arguments.items():
            if mismatch := Seq(inferred_generic_arguments.copy()[1:].values()).find(lambda t: not t.symbolic_eq(inferred_generic_argument_value[0], sm.current_scope)):
                raise SemanticErrors.GenericParameterInferredConflictInferredError().add(
                    inferred_generic_argument_name, inferred_generic_argument_value[0], mismatch).scopes(sm.current_scope)

        # Check inferred generics aren't passed explicitly. This check is present to remove redundant explicit generic
        # arguments in the code. Whilst it wouldn't have an effect on the compilation, it would be a code smell.
        for inferred_generic_argument_name, inferred_generic_argument_value in inferred_generic_arguments.items():
            if inferred_generic_argument_name in explicit_generic_arguments and inferred_generic_argument_value.length > 1:
                raise SemanticErrors.GenericParameterInferredConflictExplicitError().add(
                    inferred_generic_argument_name, inferred_generic_argument_value[0], explicit_generic_arguments[inferred_generic_argument_name]).scopes(sm.current_scope)

        # Check all the generic parameters have been inferred. Any un-inferred generic argument causes an error, because
        # the types must be known when the function is called, or the type is defined.
        for generic_parameter_name in generic_parameters.map_attr("name"):
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
                formatted_generic_arguments[generic_parameter_name] = generic_parameter_value.substituted_generics(Asts.GenericArgumentGroupAst.from_dict(formatted_generic_arguments).arguments)

        # Create the inferred generic arguments, by passing the generic arguments map into the parser, to produce a
        # GenericXXXArgumentASTs. Todo: pos_adjust?
        pos_adjust = owner.pos if owner else 0
        final_args = []
        for k, v in formatted_generic_arguments.items():
            ctor: type = GEN_MAPPING[type(generic_parameters.find(lambda g: g.name == k))]
            value = Asts.IdentifierAst.from_type(v) if isinstance(v, Asts.TypeAst) and ctor is Asts.GenericCompArgumentNamedAst else v
            final_args.append(ctor(pos=pos_adjust, name=k, value=value))

        return Seq(final_args)
