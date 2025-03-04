from __future__ import annotations

import operator
from collections import defaultdict
from typing import Dict, Optional, Tuple

from fastenum import Enum

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol, VariableSymbol
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


class FunctionConflictCheckType(Enum):
    InvalidOverload = 0
    InvalidOverride = 1


class AstFunctions:
    @staticmethod
    def get_function_owner_type_and_function_name(
            scope_manager: ScopeManager, lhs: Asts.ExpressionAst)\
            -> Tuple[Ast, Optional[Scope], Asts.IdentifierAst]:

        # Special function: ".next()" on generators.
        if isinstance(lhs, Asts.PostfixExpressionAst) and isinstance(lhs.op, Asts.PostfixExpressionOperatorStepKeywordAst):
            function_owner_type = lhs.lhs.infer_type(scope_manager).type
            function_name = Asts.IdentifierAst(lhs.op.pos, "next_")
            function_owner_scope = scope_manager.current_scope.get_symbol(function_owner_type).scope

        # Runtime access into an object: "object.method()"
        elif isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_runtime_access():
            function_owner_type = lhs.lhs.infer_type(scope_manager).type
            function_name = lhs.op.field
            function_owner_scope = scope_manager.current_scope.get_symbol(function_owner_type).scope

        # Static access into a type: "Type::method()"
        elif isinstance(lhs, Asts.PostfixExpressionAst) and lhs.op.is_static_access():
            function_owner_type = lhs.lhs
            function_name = lhs.op.field
            function_owner_scope = scope_manager.current_scope.get_symbol(function_owner_type).scope

        # Direct access into a function: "function()"
        elif isinstance(lhs, Asts.IdentifierAst):
            function_owner_type = None
            function_name = lhs
            function_owner_scope = scope_manager.current_scope.parent_module

        # Non-callable AST.
        else:
            function_owner_type = None
            function_name = None
            function_owner_scope = None

        # Return the function owner type and function name.
        return function_owner_type, function_owner_scope, function_name

    @staticmethod
    def convert_method_to_function_form(
            scope_manager: ScopeManager,
            function_owner_type: Ast, function_name: Asts.IdentifierAst, lhs: Asts.ExpressionAst,
            fn: Asts.PostfixExpressionOperatorFunctionCallAst, **kwargs)\
            -> Tuple[Asts.PostfixExpressionAst, Asts.PostfixExpressionOperatorFunctionCallAst]:

        # Create an argument for self, which is the object being called (convention tested later).
        self_argument = AstMutation.inject_code(f"{lhs.lhs}", SppParser.parse_function_call_argument_unnamed)
        function_arguments = fn.function_argument_group.arguments.copy()
        function_arguments.insert(0, self_argument)

        # Create a new function call with the object as the first argument.
        new_function_access = AstMutation.inject_code(
            f"{function_owner_type}::{function_name}",
            SppParser.parse_postfix_expression)

        new_function_call = AstMutation.inject_code(
            f"{fn.generic_argument_group}({function_arguments.join(", ")}){fn.fold_token or ""}",
            SppParser.parse_postfix_op_function_call)

        # Todo: convention too?
        new_function_call.function_argument_group.arguments[0]._type_from_self = lhs.lhs.infer_type(scope_manager).type

        # Get the overload from the uniform function call.
        return new_function_access, new_function_call

    @staticmethod
    def get_all_function_scopes(function_name: Asts.IdentifierAst, function_owner_scope: Scope, exclusive: bool = False) -> Seq[Tuple[Scope, Asts.FunctionPrototypeAst, Asts.GenericArgumentGroupAst]]:
        function_name = function_name.to_function_identifier()
        generic_argument_ctor = {VariableSymbol: Asts.GenericCompArgumentNamedAst, TypeSymbol: Asts.GenericTypeArgumentNamedAst}
        overload_scopes_and_info = Seq()

        # Functions at the module level: will have no inheritable generics (no enclosing superimposition).
        if isinstance(function_owner_scope.name, Asts.IdentifierAst):
            for ancestor_scope in function_owner_scope.ancestors:
                for sup_scope in ancestor_scope._children.filter(lambda c: isinstance(c._ast, Asts.SupPrototypeExtensionAst) and c._ast.name == function_name):
                    generics = Asts.GenericArgumentGroupAst()
                    overload_scopes_and_info.append((ancestor_scope, sup_scope._ast.body.members[0], generics))

        # Functions in a superimposition block: will have inheritable generics from "sup [...] ... { ... }".
        else:
            if isinstance(function_owner_scope._ast, Asts.ClassPrototypeAst):
                sup_scopes = function_owner_scope._direct_sup_scopes if exclusive else function_owner_scope.sup_scopes
            else:
                sup_scopes = Seq([function_owner_scope])

            for sup_scope in sup_scopes:
                for sup_ast in sup_scope._ast.body.members.filter_to_type(Asts.SupPrototypeExtensionAst).filter(lambda m: m.name == function_name):
                    generics = sup_scope._symbol_table.all().filter(lambda s: s.is_generic)
                    generics = generics.map(lambda s: generic_argument_ctor[type(s)].from_symbol(s))
                    generics = Asts.GenericArgumentGroupAst(arguments=generics)
                    overload_scopes_and_info.append((sup_scope, sup_ast._scope._ast.body.members[0], generics))

            # When a derived class has overridden a function, the overridden base class function(s) must be removed.
            for scope_1, function_1, _ in overload_scopes_and_info.copy():
                for scope_2, function_2, _ in overload_scopes_and_info.copy():
                    if function_1 is not function_2 and function_owner_scope.depth_difference(scope_1) < function_owner_scope.depth_difference(scope_2):
                        conflict = AstFunctions.check_for_conflicting_method(scope_1, scope_2, function_1, FunctionConflictCheckType.InvalidOverride)
                        if conflict:
                            overload_scopes_and_info.remove_if(lambda info: info[1] is conflict)

        # Return the overload scopes, and their generic argument groups.
        return overload_scopes_and_info

    @staticmethod
    def check_for_conflicting_method(this_scope: Scope, target_scope: Scope, new_function: Asts.FunctionPrototypeAst, conflict_type: FunctionConflictCheckType) -> Optional[Asts.FunctionPrototypeAst]:
        """
        Check for conflicting methods between the new function, anf functions in the type scope. This is used to check
        overrides are valid, and there aren't conflicting overloads.
        """

        # Get the existing superimpositions and data, and split them into scopes, functions and generics.
        existing = AstFunctions.get_all_function_scopes(new_function._orig, target_scope, conflict_type == FunctionConflictCheckType.InvalidOverload)
        existing_scopes = existing.map(operator.itemgetter(0))
        existing_functions = existing.map(operator.itemgetter(1))

        # For overloads, the required parameters must have different types or conventions.
        if conflict_type == FunctionConflictCheckType.InvalidOverload:
            parameter_filter = lambda f: f.function_parameter_group.get_req()
            parameter_comp   = lambda p1, p2, s1, s2: type(p1.convention) is type(p2.convention) and p1.type.symbolic_eq(p2.type, s1, s2)
            extra_check      = lambda f1, f2, s1, s2: f1.tok_fun == f2.tok_fun

        # For overrides, all parameters must be direct matches (type and convention). Todo: Self convention check
        else:
            parameter_filter = lambda f: f.function_parameter_group.get_non_self()
            parameter_comp   = lambda p1, p2, s1, s2: type(p1.convention) is type(p2.convention) and p1.type.symbolic_eq(p2.type, s1, s2) and p1.variable.extract_names == p2.variable.extract_names and type(p1) is type(p2)
            extra_check      = lambda f1, f2, s1, s2: f1.return_type.symbolic_eq(f2.return_type, s1, s2) and f1.tok_fun == f2.tok_fun and (type(f1.function_parameter_group.get_self().convention) is type(f2.function_parameter_group.get_self().convention) if f1.function_parameter_group.get_self() else True)

        # Check each parameter set for each overload: 1 match is a conflict.
        for existing_scope, existing_function in existing_scopes.zip(existing_functions):

            # Filter the parameters and substitute the generics.
            parameter_set_1 = parameter_filter(existing_function).deepcopy()
            parameter_set_2 = parameter_filter(new_function).deepcopy()

            # Pre-checks: parameter lengths are the sane, and the extra check passes.
            if parameter_set_1.length != parameter_set_2.length: continue
            if not extra_check(existing_function, new_function, existing_scope, this_scope): continue
            if existing_function is new_function: continue

            # Type check the parameters (0-parameter functions auto-match).
            if parameter_set_1.length + parameter_set_2.length == 0: return existing_function
            if parameter_set_1.zip(parameter_set_2).all(lambda p1p2: parameter_comp(*p1p2, existing_scope, this_scope)): return existing_function

    @staticmethod
    def name_function_arguments(arguments: Seq[Asts.FunctionCallArgumentAst], parameters: Seq[Asts.FunctionParameterAst]) -> None:

        # Get the argument names and parameter names, and check for variadic parameters.
        argument_names = arguments.filter_to_type(Asts.FunctionCallArgumentNamedAst).map_attr("name")
        parameter_names = parameters.map_attr("extract_name")
        is_variadic = parameters and isinstance(parameters[-1], Asts.FunctionParameterVariadicAst)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := argument_names.set_subtract(parameter_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(parameters[0], "parameter", invalid_argument_names[0], "argument")
        parameter_names = parameter_names.set_subtract(argument_names)

        # Name all the unnamed arguments with leftover parameter names.
        for i, unnamed_argument in arguments.filter_to_type(Asts.FunctionCallArgumentUnnamedAst).enumerate():

            # The variadic parameter requires a tuple of the remaining arguments.
            if parameter_names.length == 1 and is_variadic:
                named_argument = f"{parameter_names.pop(0)}=({arguments[i:].join(", ")})"
                named_argument = AstMutation.inject_code(named_argument, SppParser.parse_function_call_argument_named)
                arguments.replace(unnamed_argument, named_argument, 1)
                arguments.pop_n(-1, arguments.length - i - 1)
                break

            # Normal named argument assignment.
            else:
                parameter_name = parameter_names.pop(0)
                named_argument = f"${parameter_name}={unnamed_argument}"
                named_argument = AstMutation.inject_code(named_argument, SppParser.parse_function_call_argument_named)
                named_argument.name = parameter_name
                named_argument._type_from_self = unnamed_argument._type_from_self
                arguments.replace(unnamed_argument, named_argument, 1)

    @staticmethod
    def name_generic_arguments(arguments: Seq[Asts.GenericArgumentAst], parameters: Seq[Asts.GenericParameterAst], owner_type: Asts.TypeAst = None) -> None:

        # Special case for tuples to prevent infinite-recursion.
        if owner_type and owner_type.without_generics() == CommonTypes.Tup().without_generics():
            return

        # Get the argument names and parameter names, and check for variadic parameters.
        argument_names = arguments.filter_to_type(*Asts.GenericArgumentNamedAst.__args__).map(lambda a: a.name.name)
        parameter_names = parameters.map(lambda p: p.name.name)
        is_variadic = parameters and isinstance(parameters[-1], Asts.GenericParameterVariadicAst.__args__)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := argument_names.set_subtract(parameter_names):
            raise SemanticErrors.ArgumentNameInvalidError().add(parameters[0], "parameter", invalid_argument_names[0], "argument")
        parameter_names = parameter_names.set_subtract(argument_names)

        # Name all the unnamed arguments with leftover parameter names.
        for i, unnamed_argument in arguments.filter_to_type(*Asts.GenericArgumentUnnamedAst.__args__).enumerate():

            # The variadic parameter requires a tuple of the remaining arguments.
            if parameter_names.length == 1 and is_variadic:
                named_argument = f"{parameter_names.pop(0)}=({arguments[i:].join(", ")})"
                named_argument = AstMutation.inject_code(named_argument, SppParser.parse_generic_argument)
                arguments.replace(unnamed_argument, named_argument, 1)
                arguments.pop_n(-1, arguments.length - i - 1)
                break

            # Normal named argument assignment.
            else:
                try:
                    named_argument = f"{parameter_names.pop(0)}={unnamed_argument}"
                    named_argument = AstMutation.inject_code(named_argument, SppParser.parse_generic_argument)
                    named_argument.value = named_argument.value
                    arguments.replace(unnamed_argument, named_argument, 1)

                except IndexError:
                    # Too many generic arguments passed.
                    raise SemanticErrors.GenericArgumentTooManyError().add(parameters, unnamed_argument)

    @staticmethod
    def infer_generic_arguments(
            generic_parameters: Seq[Asts.GenericParameterAst],
            explicit_generic_arguments: Seq[Asts.GenericArgumentAst],
            infer_source: Dict[Asts.IdentifierAst, Asts.TypeAst],
            infer_target: Dict[Asts.IdentifierAst, Asts.TypeAst],
            scope_manager: ScopeManager,
            owner: Asts.TypeAst | Asts.ExpressionAst = None,
            variadic_parameter_identifier: Optional[Asts.IdentifierAst] = None,
            **kwargs)\
            -> Seq[Asts.GenericArgumentAst]:

        """
        cls Point[T, U, V, W] {
            x: T
            y: U
            z: V
        }

        let p = Point[W=Bool](x=1, y="hello", z=False)

        the arguments:
            generic_parameter: [T, U, V, W]
            explicit_generic_arguments: [W=Bool]
            infer_source: {x: BigInt, y: Str, z: Bool}
            infer_target: {x: T, y: U, z: V}
        """

        # Special case for tuples to prevent infinite-recursion.
        if isinstance(owner, Asts.TypeAst) and owner.without_generics() == CommonTypes.Tup().without_generics():
            return explicit_generic_arguments
        if generic_parameters.is_empty():
            return explicit_generic_arguments

        # The inferred generics map is: {TypeAst: [TypeAst]}
        inferred_generic_arguments = defaultdict(Seq)

        # Add the explicit generic arguments to the inferred generic arguments.
        for explicit_generic_argument in explicit_generic_arguments:
            inferred_generic_arguments[explicit_generic_argument.name].append(explicit_generic_argument.value)

        # Infer the generic arguments from the source to the target.
        for generic_parameter_name in generic_parameters.map_attr("name"):
            for infer_target_name, infer_target_type in infer_target.items():

                # Check for direct match (a: T vs a: BigInt).
                if infer_target_type == generic_parameter_name:
                    inferred_generic_argument = infer_source[infer_target_name]

                # Check for inner match (a: Vec[T] vs a: Vec[BigInt]).
                else:
                    corresponding_generic_parameter = infer_target_type.get_generic_parameter_for_argument(generic_parameter_name)
                    inferred_generic_argument = infer_source[infer_target_name].get_generic(corresponding_generic_parameter)

                # Handle the match if it exists.
                if inferred_generic_argument:
                    inferred_generic_arguments[generic_parameter_name].append(inferred_generic_argument)

                # Handle the variadic parameter if it exists.
                if variadic_parameter_identifier and infer_target_name == variadic_parameter_identifier:
                    inferred_generic_arguments[generic_parameter_name][-1] = inferred_generic_arguments[generic_parameter_name][-1].type_parts()[0].generic_argument_group.arguments[0].value

        # Check each generic argument name only has one unique inferred type.
        for inferred_generic_argument_name, inferred_generic_argument_value in inferred_generic_arguments.items():
            if mismatch := Seq(inferred_generic_arguments.copy()[1:].values()).find(lambda t: not t.symbolic_eq(inferred_generic_argument_value[0], scope_manager.current_scope)):
                raise SemanticErrors.GenericParameterInferredConflictInferredError().add(inferred_generic_argument_name, inferred_generic_argument_value[0], mismatch)

        # Check inferred generics aren't passed explicitly.
        for inferred_generic_argument_name, inferred_generic_argument_value in inferred_generic_arguments.items():
            if inferred_generic_argument_name in explicit_generic_arguments and inferred_generic_argument_value.length > 1:
                raise SemanticErrors.GenericParameterInferredConflictExplicitError().add(inferred_generic_argument_name, inferred_generic_argument_value[0], explicit_generic_arguments[inferred_generic_argument_name])

        # Check all the generic parameters have been inferred.
        for generic_parameter_name in generic_parameters.map_attr("name"):
            if generic_parameter_name not in inferred_generic_arguments:
                raise SemanticErrors.GenericParameterNotInferredError().add(generic_parameter_name, owner)

        # Create the inferred generic arguments.
        inferred_generic_arguments = {k: v[0] for k, v in inferred_generic_arguments.items()}
        inferred_generic_arguments = [AstMutation.inject_code(f"{k}={v}", SppParser.parse_generic_argument) for k, v in inferred_generic_arguments.items()]
        return Seq(inferred_generic_arguments)
