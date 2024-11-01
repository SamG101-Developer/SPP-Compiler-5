from __future__ import annotations
from collections import defaultdict
from typing import Dict, Optional, Tuple, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentAst import FunctionCallArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentNamedAst import FunctionCallArgumentNamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterAst import FunctionParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericArgumentAst, GenericArgumentNamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentGroupAst import GenericArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionAst import PostfixExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionOperatorFunctionCallAst import PostfixExpressionOperatorFunctionCallAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class AstFunctions:
    @staticmethod
    def get_function_owner_type_and_function_name(
            scope_manager: ScopeManager, lhs: ExpressionAst)\
            -> Tuple[Ast, Optional[Scope], IdentifierAst]:

        # Todo: Change to look for FunMov/FunMut/FunRef implementations over the $Field type?
        from SPPCompiler.SemanticAnalysis import PostfixExpressionAst

        # Runtime access into an object: "object.method()"
        if isinstance(lhs, PostfixExpressionAst) and lhs.op.is_runtime_access():
            function_owner_type = lhs.lhs.infer_type(scope_manager)
            function_name = lhs.op.field
            function_owner_scope = None

        # Static access into a type: "Type::method()"
        elif isinstance(lhs, PostfixExpressionAst) and lhs.op.is_static_access():
            function_owner_type = lhs.lhs
            function_name = lhs.op.field
            function_owner_scope = scope_manager.current_scope.get_symbol(function_owner_type).scope

        # Direct access into a function: "function()"
        elif isinstance(lhs, IdentifierAst):
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
    def convert_function_to_type_access(
            scope_manager: ScopeManager,
            function_owner_type: Ast, function_name: IdentifierAst, lhs: ExpressionAst,
            fn: PostfixExpressionOperatorFunctionCallAst, **kwargs)\
            -> None:

        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Create an argument for self, which is the object being called (convention tested later).
        self_argument = AstMutation.inject_code(f"{lhs.lhs}", Parser.parse_function_call_argument_unnamed)
        function_arguments = fn.function_argument_group.arguments.copy()
        function_arguments.insert(0, self_argument)

        # Create a new function call with the object as the first argument.
        new_function_access = AstMutation.inject_code(
            f"{function_owner_type}::{function_name}",
            Parser.parse_postfix_expression)

        new_function_call = AstMutation.inject_code(
            f"{fn.generic_argument_group}{fn.function_argument_group}{fn.fold_token or ""}",
            Parser.parse_postfix_op_function_call)

        # Get the overload from the uniform function call.
        fn._overload = new_function_call.determine_overload(scope_manager, new_function_access, **kwargs)

    @staticmethod
    def get_all_function_scopes(function_name: IdentifierAst, function_owner_scope: Scope, exclusive: bool = False) -> Seq[Tuple[Scope, GenericArgumentGroupAst]]:
        from SPPCompiler.SemanticAnalysis import TypeAst

        converted_identifier = TypeAst.from_function_identifier(function_name)
        overload_scopes_and_info = Seq()

        # Functions at the module level: will have no inheritable generics (no enclosing superimposition).
        if isinstance(function_name, TypeAst):
            for scope in function_owner_scope.ancestors:
                if scope.children.map_attr("name").contains(converted_identifier):
                    sup_scope = scope.children.find(lambda s: s.name == converted_identifier)
                    empty_generic_group = GenericArgumentGroupAst.default()
                    overload_scopes_and_info.append((sup_scope, empty_generic_group))

        # Functions in a superimposition block: will have inheritable generics from "sup [...] ... { ... }".
        else:
            for sup_scope in function_owner_scope._direct_sup_scopes if exclusive else function_owner_scope.sup_scopes:
                if fun_scope := sup_scope._ast.body.members.filter_to_type(SupPrototypeInheritance).filter(lambda m: m.name == function_name):
                    generics = sup_scope._symbol_table.all().filter_to_type(TypeSymbol).filter(lambda t: t.is_generic and t.scope)
                    generics = generics.map(GenericArgumentNamedAst.from_symbol)
                    generics = GenericArgumentGroupAst.default(generics)
                    overload_scopes_and_info.append((fun_scope, generics))

        # Return the overload scopes, and their generic argument groups.
        return overload_scopes_and_info

    @staticmethod
    def name_function_arguments(arguments: Seq[FunctionCallArgumentAst], parameters: Seq[FunctionParameterAst]) -> None:
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentNamedAst, FunctionCallArgumentUnnamedAst
        from SPPCompiler.SemanticAnalysis import FunctionParameterVariadicAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Get the argument names and parameter names, and check for variadic parameters.
        argument_names = arguments.filter_to_type(FunctionCallArgumentNamedAst).map_attr("name")
        parameter_names = parameters.map_attr("name")
        is_variadic = parameters and isinstance(parameters[-1], FunctionParameterVariadicAst)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := argument_names.set_subtract(parameter_names):
            raise AstErrors.INVALID_ARGUMENT_NAMES(invalid_argument_names)
        parameter_names = parameter_names.set_subtract(argument_names)

        # Name all the unnamed arguments with leftover parameter names.
        for i, unnamed_argument in arguments.filter_to_type(FunctionCallArgumentUnnamedAst).enumerate():

            # The variadic parameter requires a tuple of the remaining arguments.
            if parameter_names.length == 1 and is_variadic:
                named_argument = f"{parameter_names.pop(0)}=({arguments[i:].join(", ")})"
                named_argument = AstMutation.inject_code(named_argument, Parser.parse_function_call_argument_named)
                arguments.replace(unnamed_argument, named_argument, 1)
                arguments.pop_n(arguments.length - i - 1)
                break

            # Normal named argument assignment.
            else:
                named_argument = f"{parameter_names.pop(0)}={unnamed_argument}"
                named_argument = AstMutation.inject_code(named_argument, Parser.parse_function_call_argument_named)
                arguments.replace(unnamed_argument, named_argument, 1)

    @staticmethod
    def name_generic_arguments(arguments: Seq[GenericArgumentAst], parameters: Seq[GenericParameterAst], owner_type: TypeAst = None) -> None:
        from SPPCompiler.SemanticAnalysis import GenericArgumentUnnamedAst, GenericArgumentNamedAst
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentUnnamedAst, GenericTypeArgumentUnnamedAst
        from SPPCompiler.SemanticAnalysis import GenericParameterVariadicAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Special case for tuples to prevent infinite-recursion.
        if owner_type and owner_type.without_generics() == CommonTypes.Tup().without_generics():
            return

        # Get the argument names and parameter names, and check for variadic parameters.
        argument_names = arguments.filter_to_type(*GenericArgumentNamedAst.__value__.__args__).map_attr("name")
        parameter_names = parameters.map_attr("name")
        is_variadic = parameters and isinstance(parameters[-1], GenericParameterVariadicAst.__value__.__args__)

        # Check for invalid argument names against parameter names, then remove the valid ones.
        if invalid_argument_names := argument_names.set_subtract(parameter_names):
            raise AstErrors.INVALID_ARGUMENT_NAMES(invalid_argument_names)
        parameter_names = parameter_names.set_subtract(argument_names)

        # Create a construction mapping from unnamed to named generic arguments (parser functions for code injection).
        GenericArgumentCTor = {
            GenericCompArgumentUnnamedAst: Parser.parse_generic_comp_argument_named,
            GenericTypeArgumentUnnamedAst: Parser.parse_generic_type_argument_named}

        # Name all the unnamed arguments with leftover parameter names.
        for i, unnamed_argument in arguments.filter_to_type(*GenericArgumentUnnamedAst.__value__.__args__).enumerate():

            # The variadic parameter requires a tuple of the remaining arguments.
            if parameter_names.length == 1 and is_variadic:
                named_argument = f"{parameter_names.pop(0)}=({arguments[i:].join(", ")})"
                named_argument = AstMutation.inject_code(named_argument, GenericArgumentCTor[type(unnamed_argument)])
                arguments.replace(unnamed_argument, named_argument, 1)
                arguments.pop_n(arguments.length - i - 1)
                break

            # Normal named argument assignment.
            else:
                named_argument = f"{parameter_names.pop(0)}={unnamed_argument}"
                named_argument = AstMutation.inject_code(named_argument, GenericArgumentCTor[type(unnamed_argument)])
                arguments.replace(unnamed_argument, named_argument, 1)

        print(arguments)

    @staticmethod
    def inherit_generic_arguments(
            generic_parameters: Seq[GenericParameterAst],
            explicit_generic_arguments: Seq[GenericArgumentAst],
            infer_source: Dict[IdentifierAst, TypeAst],
            infer_target: Dict[IdentifierAst, TypeAst],
            scope_manager: ScopeManager, **kwargs)\
            -> Seq[GenericArgumentAst]:

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

        from SPPCompiler.SemanticAnalysis import TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # The inferred generics map is: {TypeAst: [TypeAst]}
        inferred_generic_arguments = defaultdict(Seq)

        # Add the explicit generic arguments to the inferred generic arguments.
        for explicit_generic_argument in explicit_generic_arguments:
            inferred_generic_arguments[explicit_generic_argument.name].append(explicit_generic_argument.value)

        # Infer the generic arguments from the source to the target.
        for infer_source_name, infer_source_type in infer_source.items():
            infer_target_type = infer_target[infer_source_name]
            inferred_generic_arguments[infer_target_type].append(infer_source_type)

        # Check each generic argument name only has one unique inferred type.
        for inferred_generic_argument in inferred_generic_arguments.copy().values():
            if mismatch := Seq(inferred_generic_arguments.copy()[1:].values()).find(lambda t: not t.symbolic_eq(inferred_generic_argument[0], scope_manager.current_scope)):
                raise AstErrors.CONFLICTING_GENERIC_INFERENCE(inferred_generic_arguments[0], mismatch)

        # Check inferred generics aren't passed explicitly.
        for inferred_generic_argument_name, inferred_generic_argument_type in inferred_generic_arguments.items():
            if inferred_generic_argument_name in explicit_generic_arguments and inferred_generic_argument_type.length > 1:
                raise AstErrors.EXPLICIT_GENERIC_INFERENCE(inferred_generic_argument_name)

        # Check all the generic parameters have been inferred.
        for generic_parameter in generic_parameters:
            if generic_parameter.name not in inferred_generic_arguments:
                raise AstErrors.UNINFERRED_GENERIC_PARAMETER(generic_parameter)

        # Create a construction mapping from unnamed to named generic arguments (parser functions for code injection).
        GenericArgumentCTor = defaultdict(
            lambda: Parser.parse_generic_comp_argument_named, {TypeAst: Parser.parse_generic_type_argument_named})

        # Create the inferred generic arguments.
        inferred_generic_arguments = {k: v[0] for k, v in inferred_generic_arguments.items()}
        inferred_generic_arguments = [AstMutation.inject_code(f"{k}={v}", GenericArgumentCTor[type(v)]) for k, v in inferred_generic_arguments.items()]
        return Seq(inferred_generic_arguments)
