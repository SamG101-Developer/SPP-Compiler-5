from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional, Tuple, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentGroupAst import FunctionCallArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentGroupAst import GenericArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionOperatorFunctionCallAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    generic_argument_group: GenericArgumentGroupAst
    function_argument_group: FunctionCallArgumentGroupAst
    fold_token: Optional[TokenAst]

    _overload: Optional[Tuple[FunctionPrototypeAst, Scope]] = field(default=None, init=False, repr=False)
    _is_async: Optional[Ast] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentGroupAst, GenericArgumentGroupAst

        # Create defaults.
        self.generic_argument_group = self.generic_argument_group or GenericArgumentGroupAst.default()
        self.function_argument_group = self.function_argument_group or FunctionCallArgumentGroupAst.default()

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.generic_argument_group.print(printer),
            self.function_argument_group.print(printer),
            self.fold_token.print(printer) if self.fold_token else ""]
        return "".join(string)

    def determine_overload(self, scope_manager: ScopeManager, lhs: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentNamedAst, PostfixExpressionAst
        from SPPCompiler.SemanticAnalysis import FunctionParameterSelfAst, FunctionParameterVariadicAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.Utils.Errors import SemanticError

        # 3 types of function calling: function_call(), obj.method_call(), Type::static_method_call(). Determine the
        # function's name and its owner type/namespace.
        function_owner_type, function_owner_scope, function_name = AstFunctions.get_function_owner_type_and_function_name(scope_manager, lhs)
        if not function_name:
            raise AstErrors.UNCALLABLE_AST(lhs)

        # Convert the obj.method_call(...args) into Type::method_call(obj, ...args).
        if isinstance(lhs, PostfixExpressionAst) and lhs.op.is_runtime_access():
            AstFunctions.convert_function_to_type_access(scope_manager, function_owner_type, function_name, lhs, self, **kwargs)
            return

        # Record the "pass" and "fail" overloads
        all_overloads = AstFunctions.get_all_function_scopes(function_name, function_owner_scope)
        pass_overloads = Seq()
        fail_overloads = Seq()

        for function_scope, owner_scope_generic_arguments in all_overloads:
            function_overload: FunctionPrototypeAst = function_scope._ast

            # Extract generic/function parameter information from the overload.
            parameters = function_overload.function_parameter_group.parameters.copy()
            parameter_names = parameters.map_attr("extract_name")
            parameter_names_req = function_overload.function_parameter_group.get_req().map_attr("name")
            generic_parameters = function_overload.generic_parameter_group.parameters.map_attr("name")
            is_variadic = function_overload.function_parameter_group.get_var() is not None

            # Extract generic/function argument information from this AST.
            arguments = self.function_argument_group.arguments.copy()
            argument_names = arguments.filter_to_type(FunctionCallArgumentNamedAst).map_attr("name")
            generic_arguments = self.generic_argument_group.arguments.copy()

            # Use a try-except block to catch any errors as a following overload could still be valid.
            try:
                # Can't call an abstract function.
                if function_overload._abstract:
                    ...

                # Can't call non-implemented functions (dummy functions).
                if function_overload._non_implemented:
                    ...

                # Check if there are too many arguments for the function (non-variadic).
                if arguments.length > parameters.length and not is_variadic:
                    ...

                # Check for any named arguments without a corresponding parameter.
                if invalid_arguments := argument_names.set_subtract(parameter_names):
                    ...

                # Remove all the used parameters names from the set of parameter names, and name the unnamed arguments.
                AstFunctions.name_function_arguments(arguments, parameters)
                AstFunctions.name_generic_arguments(generic_arguments, generic_parameters)
                argument_names = arguments.map_attr("name")

                # Check if there are too few arguments for the function (by missing names).
                if missing_parameters := parameter_names_req.set_subtract(argument_names):
                    ...

                # Infer generic arguments and inherit from the function owner block.
                generic_arguments = AstFunctions.inherit_generic_arguments(
                    generic_parameters=function_overload.generic_parameter_group.get_req(),
                    explicit_generic_arguments=generic_arguments + owner_scope_generic_arguments,
                    infer_source=arguments.map(lambda a: (a.name, a.infer_type(scope_manager, **kwargs).type)).dict(),
                    infer_target=parameters.map(lambda p: (p.extract_name, p.type)).dict(),
                    scope_manager=scope_manager, **kwargs)

                # Create a new overload with the generic arguments applied.
                if generic_arguments:
                    new_overload = copy.deepcopy(function_overload)
                    new_overload.generic_parameter_group.parameters = Seq()
                    new_overload.function_parameter_group.parameters.for_each(lambda p: p.type.sub_generics(generic_arguments))
                    new_overload.return_type.sub_generics(generic_arguments)
                    parameters = new_overload.function_parameter_group.parameters.copy()
                    function_overload = new_overload

                # Type check the arguments against the parameters.
                sorted_arguments = arguments.sort(key=lambda a: parameter_names.index(a.name))
                for argument, parameter in sorted_arguments.zip(parameters):
                    argument_type = argument.infer_type(scope_manager, **kwargs)
                    parameter_type = InferredType(convention=type(parameter.convention), type=parameter.type)

                    if isinstance(parameter, FunctionParameterSelfAst):
                        argument_type.convention = parameter_type.convention
                        argument.convention = parameter.convention

                    elif not parameter_type.symbolic_eq(argument_type, function_scope, scope_manager.current_scope):
                        raise AstErrors.TYPE_MISMATCH(parameter, parameter_type, argument, argument_type)

                # Mark the overload as a pass.
                pass_overloads.append((function_scope, function_overload))

            except SemanticError as e:
                # Mark the overload as a fail.
                fail_overloads.append((function_scope, function_overload, e))
                continue

        # If there are no pass overloads, raise an error.
        if pass_overloads.is_empty():
            failed_signatures_and_errors = fail_overloads.map(lambda f: f[1].print_signature() + f" - {f[2].tag}").join("\n")
            raise AstErrors.NO_VALID_FUNCTION_SIGNATURES(self, failed_signatures_and_errors)

        # If there are multiple pass overloads, raise an error.
        elif pass_overloads.length > 1:
            passed_signatures = pass_overloads.map(lambda f: f[1].print_signature()).join("\n")
            raise AstErrors.AMBIGUOUS_FUNCTION_SIGNATURES(self, passed_signatures)

        # Set the overload to the only pass overload.
        self._overload = pass_overloads[0]

    def infer_type(self, scope_manager: ScopeManager, lhs: ExpressionAst = None, **kwargs) -> InferredType:
        # Expand the return type from the scope it was defined in => comparisons won't require function scope knowledge.
        _, function_owner_scope, _ = AstFunctions.get_function_owner_type_and_function_name(scope_manager, lhs)
        return_type = self._overload[1].return_type
        return_type = function_owner_scope.get_symbol(return_type).fully_qualified
        return InferredType.from_type(return_type)

    def analyse_semantics(self, scope_manager: ScopeManager, lhs: ExpressionAst = None, **kwargs) -> None:
        self.function_argument_group.analyse_pre_semantics(scope_manager, **kwargs)
        self.determine_overload(scope_manager, lhs, **kwargs)  # Also adds the "self" argument if needed.
        self.generic_argument_group.analyse_semantics(scope_manager, **kwargs)
        self.function_argument_group.analyse_semantics(scope_manager, target=self._overload[0], is_async=self._is_async, **kwargs)


__all__ = ["PostfixExpressionOperatorFunctionCallAst"]
