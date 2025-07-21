from __future__ import annotations

import itertools
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import NoReturn, Optional, TYPE_CHECKING, Tuple

from colorama import Fore, Style

from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class SemanticError(BaseException):
    class Format(Enum):
        NORMAL = 0
        MINIMAL = 1
        NONE = 2

    @dataclass(slots=True)
    class ErrorInfo:
        ast: Asts.Ast
        tag: str
        msg: str
        tip: str
        fmt: SemanticError.Format

    error_info: list[ErrorInfo]
    error_formatters: list[ErrorFormatter]

    def __init__(self, *args) -> None:
        super().__init__(args)
        self.error_info = []

    @abstractmethod
    def add(self, *args, **kwargs) -> SemanticError:
        return self

    def scopes(self, *scopes) -> SemanticError:
        # Register the error formatters against the instance.
        self.error_formatters = [scope._error_formatter for scope in scopes]
        return self

    def add_error(self, ast: Asts.Ast, tag: str, msg: str, tip: str, fmt: Format = Format.NORMAL) -> SemanticError:
        # Add an error into the output list.
        self.error_info.append(SemanticError.ErrorInfo(ast, tag, msg, tip, fmt))
        return self

    def add_info(self, ast: Asts.Ast, tag: str) -> SemanticError:
        # Add an info message (minimal error metadata) into the output list.
        self.add_error(ast, tag, "", "", SemanticError.Format.MINIMAL)
        return self

    def _format_message(self, error_info: ErrorInfo) -> (str, bool):
        # For minimal formatting, the message remains empty, as a "tag" is provided.
        if error_info.fmt == SemanticError.Format.MINIMAL:
            return "", True

        # Otherwise, combine the message and tip into a single color-formatted string.
        f = f"\n{Style.BRIGHT}  = err : {type(self).__name__}\n  = note: {Style.NORMAL}{error_info.msg}\n{Fore.LIGHTCYAN_EX}{Style.BRIGHT}  = help: {Style.NORMAL}{error_info.tip}{Fore.RESET}"
        return f, False

    def throw(self) -> NoReturn:
        # Format the error messages and raise the error.
        # Todo: tidy this loop up
        error_message = "\n\n"
        cycle = itertools.cycle(self.error_formatters)
        for error, error_formatter in zip(self.error_info, [next(cycle) for i in range(len(self.error_info))]):
            formatted_message, is_minimal = self._format_message(error)
            error_message += error_formatter.error_ast(error.ast, formatted_message, error.tag, is_minimal)
        print(error_message)
        raise type(self)()


class SemanticErrors:
    class AnnotationInvalidLocationError(SemanticError):
        """
        The AnnotationInvalidLocationError is raised if a standard annotation is applied to a non-compatible AST. This
        includes applying the "@public" annotation to a superimposition, or the "@no_impl" method annotation to a class.
        An allowlist of valid ASTs for the annotation is provided in the error message.
        """

        def add(self, annotation: Asts.IdentifierAst, applied_to: Asts.Ast, block_list: str) -> SemanticError:
            self.add_info(
                ast=annotation,
                tag=f"Annotation '{annotation}' defined here")

            self.add_error(
                ast=applied_to,
                tag=f"Invalid {block_list} context defined here.",
                msg=f"This annotation can not be applied here.",
                tip=f"Remove the annotation from here.")

            return self

    class AnnotationInvalidError(SemanticError):
        """
        The AnnotationInvalidError is raised if a non-standard annotation is used in the code. This includes using the
        "@foo" annotation, which is not a valid annotation in the language. Only standard annotations are allowed, such
        as "@public", "@no_impl" etc.
        """

        def add(self, annotation: Asts.IdentifierAst) -> SemanticError:
            self.add_error(
                ast=annotation,
                tag="Invalid annotation.",
                msg=f"This annotation is unknown.",
                tip=f"Remove the annotation from here.")

            return self

    class AnnotationConflictError(SemanticError):
        """
        The AnnotationConflictError is raised if there are 2 annotations on the same object that either have conflicting
        behaviour / are mutually exclusive. For example, using "@hot" and "@cold" on the same function would raise this
        error.
        """

        def add(
                self, first_annotation: Asts.IdentifierAst,
                conflicting_annotation: Asts.IdentifierAst) -> SemanticError:
            self.add_info(
                ast=first_annotation,
                tag=f"Annotation '{first_annotation}' applied here")

            self.add_error(
                ast=conflicting_annotation,
                tag="Conflicting annotation.",
                msg=f"The annotation '{conflicting_annotation}' conflicts with the first annotation.",
                tip=f"Remove the conflicting annotation.")

            return self

    class IdentifierDuplicationError(SemanticError):
        """
        The IdentifierDuplicationError is raised if the same identifier is defined multiple times in the same context.
        This could be for class attributes, function parameter names, generic parameter names etc.
        """

        def add(
                self, first_occurrence: Asts.Ast, second_occurrence: Asts.Ast, what: str) -> SemanticError:
            self.add_info(
                ast=first_occurrence,
                tag=f"{what.capitalize()} '{first_occurrence}' defined here")

            self.add_error(
                ast=second_occurrence,
                tag=f"Duplicate {what}.",
                msg=f"The {what} '{second_occurrence}' is already defined.",
                tip=f"Remove or rename the duplicate {what}.")

            return self

    class OrderInvalidError(SemanticError):
        """
        The OrderInvalidError is raised if a collection of ASTs is in the wrong order. This includes optional parameters
        before required parameters, or named arguments before unnamed arguments.
        """

        def add(self, first_what: str, first: Asts.Ast, second_what: str, second: Asts.Ast, what: str) -> SemanticError:
            self.add_info(
                ast=first,
                tag=f"{first_what.capitalize()} {what} '{first}' defined here")

            self.add_error(
                ast=second,
                tag=f"Invalid {what} order.",
                msg=f"The {second_what.lower()} {what} '{second}' is in the wrong position.",
                tip=f"Move the {second_what.lower()} {what} to after the {first_what.lower()} {what}.")

            return self

    class ParameterMultipleSelfError(SemanticError):
        """
        The ParameterMultipleSelfError is raised if there are multiple "self" parameters in a function definition. A
        maximum one "self" parameter is allowed per function.
        """

        def add(
                self, first_self_parameter: Asts.FunctionParameterAst,
                second_self_parameter: Asts.FunctionParameterAst) -> SemanticError:
            self.add_info(
                ast=first_self_parameter,
                tag=f"Self parameter defined here")

            self.add_error(
                ast=second_self_parameter,
                tag=f"Second 'self' parameter.",
                msg="Only one 'self' parameter is allowed.",
                tip="Remove the second 'self' parameter.")

            return self

    class ParameterSelfOutsideSuperimpositionError(SemanticError):
        """
        The ParameterSelfOutsideSuperimpositionError is raised if a "self" parameter is used outside of a
        superimposition, ie in a module-level free function.
        """

        def add(self, self_parameter: Asts.FunctionParameterAst, function: Asts.FunctionPrototypeAst) -> SemanticError:
            self.add_info(
                ast=function,
                tag="Function defined here")

            self.add_error(
                ast=self_parameter,
                tag="Self parameter outside superimposition.",
                msg="The 'self' parameter can only be used in superimpositions.",
                tip="Remove the 'self' parameter.")

            return self

    class ParameterMultipleVariadicError(SemanticError):
        """
        The ParameterMultipleVariadicError is raised if there are multiple variadic parameters in a function definition.
        A maximum one variadic parameter is allowed per function.
        """

        def add(
                self, first_variadic_parameter: Asts.FunctionParameterAst,
                second_variadic_parameter: Asts.FunctionParameterAst) -> SemanticError:
            self.add_info(
                ast=first_variadic_parameter,
                tag=f"Variadic parameter '{first_variadic_parameter}' defined here")

            self.add_error(
                ast=second_variadic_parameter,
                tag=f"Second variadic parameter '{second_variadic_parameter}.",
                msg="Only one variadic parameter is allowed.",
                tip="Remove the second variadic parameter.")

            return self

    class FunctionCoroutineInvalidReturnTypeError(SemanticError):
        """
        The FunctionCoroutineInvalidReturnTypeError is raised if a coroutine has a return type that is not a generator.
        All coroutines must return Gen[T] (with optional generic type parameters).
        """

        def add(self, return_type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                ast=return_type,
                tag="Invalid coroutine return type.",
                msg="The return type of a coroutine must be a generator.",
                tip="Change the return type to the 'Gen' type.")

            return self

    class FunctionCoroutineContainsReturnStatementError(SemanticError):
        """
        The FunctionCoroutineContainsRetError is raised if a coroutine contains a return statement with an expression.
        Coroutines cannot contain "ret" statements with expressions, only empty "ret" statements or "gen" expressions,
        which yield a value. The actual generator is implicitly returned as soon as the function is called.
        """

        def add(self, coroutine_definition: Asts.TokenAst, expression: Asts.ExpressionAst) -> SemanticError:
            self.add_info(
                ast=coroutine_definition,
                tag="Coroutine defined here")

            self.add_error(
                ast=expression,
                tag="Return statement with expression in coroutine.",
                msg="Coroutines cannot return values.",
                tip="Remove the attached expression.")

            return self

    class FunctionSubroutineContainsGenExpressionError(SemanticError):
        """
        The FunctionSubroutineContainsGenError is raised if a subroutine contains a "gen" expression. Subroutines cannot
        contain "gen" expressions, only "ret" statements, which return a value.
        """

        def add(self, subroutine_definition: Asts.TokenAst, gen_expression: Asts.TokenAst) -> SemanticError:
            self.add_info(
                ast=subroutine_definition,
                tag="Subroutine defined here")

            self.add_error(
                ast=gen_expression,
                tag="Gen expression in subroutine.",
                msg="Subroutines cannot contain gen expressions.",
                tip="Remove the gen expression.")

            return self

    class FunctionSubroutineMissingReturnStatementError(SemanticError):
        """
        The FunctionSubroutineMissingRetError is raised if a non-void-returning subroutine does not contain a return
        statement.
        """

        def add(self, final_member: Asts.TokenAst, return_type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=final_member,
                tag="Non-ret statement found here")

            self.add_error(
                ast=return_type,
                tag="Missing return statement.",
                msg="Non-void subroutines must return a value.",
                tip="Add a return statement to the subroutine.")

            return self

    class FunctionPrototypeConflictError(SemanticError):
        """
        The FunctionPrototypeConflictError is raised if there are multiple function prototypes with an equal signature.
        There are certain criteria such as conventions and parameter types that have to match for a function to be
        considered a duplicate.
        """

        def add(self, first_prototype: Asts.IdentifierAst, second_prototype: Asts.IdentifierAst) -> SemanticError:
            self.add_info(
                ast=first_prototype,
                tag="First prototype defined here")

            self.add_error(
                ast=second_prototype,
                tag="Duplicate prototype.",
                msg="The function prototype conflicts with another prototype.",
                tip="Remove the duplicate prototype.")

            return self

    class ArgumentNameInvalidError(SemanticError):
        """
        The ArgumentNameInvalidError is raised if a named argument has been provided with a name that is not valid based
        on the target. This would be parameter vs argument name or attribute vs object initialization argument name. The
        source is the parameter/attribute, and the target is the argument.
        """

        def add(self, target: Asts.Ast, what_target: str, source: Asts.Ast, what_source: str) -> SemanticError:
            if target:
                self.add_info(
                    ast=target,
                    tag=f"{what_target.capitalize()} '{target}' defined here")

            self.add_error(
                ast=source,
                tag=f"Invalid {what_source} name for '{source}'.",
                msg=f"{what_target}/{what_source} name mismatch.",
                tip="Use a name found on the target.")

            return self

    class ArgumentRequiredNameMissingError(SemanticError):
        """
        The ArgumentRequiredNameMissingError is raised if a required named argument is missing from a function call or
        object initialization. This would be a parameter vs argument name or attribute vs object initialization argument
        name. The source is the parameter/attribute, and the target is the argument.
        """

        def add(self, where: Asts.Ast, target: Asts.Ast, what_target: str, what_source: str) -> SemanticError:
            self.add_info(
                ast=target,
                tag=f"{what_target.capitalize()} defined here")

            self.add_error(
                ast=where,
                tag=f"Missing {what_source} name.",
                msg=f"Missing the {what_source} '{target}'.",
                tip=f"Add the missing {what_target} name.")

            return self

    class ArgumentTupleExpansionOfNonTupleError(SemanticError):
        """
        The ArgumentTupleExpansionOfNonTupleError is raised if a tuple expansion is used on a non-tuple type. Tuple
        expansions can only be used on tuples, such as "f(..tuple_argument)".
        """

        def add(self, expansion_arg: Asts.Ast, arg_type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                ast=expansion_arg,
                tag=f"Type inferred as '{arg_type}' here",
                msg="Tuple expansions can only be used on tuples.",
                tip="Remove the '..' from the argument.")

            return self

    class FunctionCallNoValidSignaturesError(SemanticError):
        """
        The FunctionCallNoValidSignaturesError is raised if a function call has no valid signatures that match the
        arguments provided. A list of valid signatures is provided in the error message.
        """

        def add(self, function_call: Asts.Ast, signatures: str, attempted: str) -> SemanticError:
            self.add_error(
                ast=function_call,
                tag="Invalid arguments for function call",
                msg="There are no overloads accepting the given arguments",
                tip=f"\n\t{signatures.replace("\n", "\n\t")}\n\nAttempted signature:\n\t{attempted}")

            return self

    class GenericArgumentTooManyError(SemanticError):
        """
        The GenericArgumentTooManyError is raised if a function call has too many generic arguments. This can be from a
        type definition, or a function call.
        """

        def add(
                self, generic_parameters: list[Asts.GenericParameterAst], owner: Asts.Ast,
                extra_generic_argument: Asts.GenericArgumentAst) -> SemanticError:
            self.add_info(
                ast=generic_parameters[0] if generic_parameters else owner,
                tag=f"Generic parameters defined here for '{owner}'")

            self.add_error(
                ast=extra_generic_argument,
                tag="Extra generic argument provided here.",
                msg="Too many generic arguments.",
                tip="Remove the extra generic argument.")

            return self

    class GenericArgumentIncorrectVariationError(SemanticError):
        """
        The GenericParameterIncorrectVariationError is raised if a generic type argument is used to match a generic comp
        parameter or vice versa.
        """

        def add(
                self, generic_parameter: Asts.GenericParameterAst, generic_argument: Asts.GenericArgumentAst,
                owner: Asts.Ast) -> SemanticError:

            self.add_info(
                ast=generic_parameter,
                tag=f"Generic parameter defined here for '{owner}'")

            self.add_error(
                ast=generic_argument,
                tag="Generic argument does not match generic parameter.",
                msg="The generic argument is not compatible with the generic parameter.",
                tip="Use a compatible generic argument.")

            return self

    class FunctionCallAmbiguousSignaturesError(SemanticError):
        """
        The FunctionCallAmbiguousSignaturesError is raised if a function call has multiple valid signatures that match
        the arguments provided. This is caused by generic substitution causing a match with multiple overloads. Concrete
        types signature conflicts are detected on function prototype analysis.
        """

        def add(self, function_call: Asts.Ast, signatures: str, attempted: str) -> SemanticError:
            self.add_error(
                ast=function_call,
                tag="Ambiguous function call",
                msg="There are multiple overloads accepting the given arguments",
                tip=f"\n\t{signatures.replace("\n", "\n\t")}\n\nAttempted signature:\n\t{attempted}")

            return self

    class FunctionCallAbstractFunctionError(SemanticError):
        """
        The FunctionCallAbstractFunctionError is raised if an abstract function is called. Abstract functions cannot be
        called directly, as they have no implementation. Instead, they must be called on a subtype that provides an
        implementation.
        """

        def add(
                self, function: Asts.IdentifierAst,
                function_call: Asts.PostfixExpressionOperatorFunctionCallAst) -> SemanticError:
            self.add_info(
                ast=function,
                tag="Function annotated as abstract")

            self.add_error(
                ast=function_call,
                tag="Abstract method called here.",
                msg="Cannot call abstract methods.",
                tip="Call the method on a subtype")

            return self

    class FunctionCallTooManyArgumentsError(SemanticError):
        """
        The FunctionCallTooManyArgumentsError is raised if a function call has too many arguments.
        Todo: add more info?
        """

        def add(
                self, function_call: Asts.PostfixExpressionOperatorFunctionCallAst,
                function_definition: Asts.IdentifierAst) -> SemanticError:
            self.add_info(
                ast=function_definition,
                tag="Function defined here")

            self.add_error(
                ast=function_call,
                tag="Too many arguments.",
                msg="The function call has too many arguments.",
                tip="Remove the extra arguments.")

            return self

    class UnreachableCodeError(SemanticError):
        """
        The UnreachableCodeError is raised if there is code after a skip/exit/ret keyword in the same scope. This code
        is unreachable as the keyword always exits the scope into the parent scope.
        """

        def add(self, return_ast: Asts.RetStatementAst, next_ast: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=return_ast,
                tag="Return statement defined here")

            self.add_error(
                ast=next_ast,
                tag="Unreachable code.",
                msg="The code after the return statement is unreachable.",
                tip="Remove the unreachable code or move the return statement.")

            return self

    class NumberOutOfBoundsError(SemanticError):
        """
        The NumberOutOfBoundsError is raised if a number is out of the valid range for the type. This includes integer
        literals that are too large or too small, and float literals that are too large or too small.
        """

        def add(
                self, number: Asts.IntegerLiteralAst | Asts.FloatLiteralAst, minimum: int, maximum: int,
                what: str) -> SemanticError:
            self.add_error(
                ast=number,
                tag=f"{what.capitalize()} out of range.",
                msg=f"The {what} '{number}' is out of range [{minimum}, {maximum}].",
                tip=f"Change the number to be within the range, or change the type specifier.")

            return self

    class IdentifierUnknownError(SemanticError):
        """
        The IdentifierUnknownError is raised if an identifier is used that is not defined in the current scope. This
        could be a variable, attribute, namespace, type etc.
        """

        def add(self, identifier: Asts.Ast, what: str, closest_match: Optional[str]) -> SemanticError:
            self.add_error(
                ast=identifier,
                tag=f"Undefined {what}: '{identifier}'.",
                msg=f"The {what} '{identifier}' is not defined.",
                tip=f"Did you mean '{closest_match}'?" if closest_match else f"Define the {what}.")

            return self

    class AmbiguousMemberAccessError(SemanticError):
        """
        The AmbiguousMemberAccessError is raised if a member access is ambiguous, meaning that there are multiple
        members with the same name at the highest level. For example, if A inherits from B and C, and both B and C
        define the attribute "x", then accessing "A.x" would be ambiguous, as it is not clear which "x" is being
        accessed. But if A also has an "x" attribute, then it is clear that "A.x" refers to A's own "x" attribute.
        """

        def add(
                self, first: Asts.IdentifierAst, second: Asts.IdentifierAst,
                field: Asts.IdentifierAst | Asts.TypeIdentifierAst) -> SemanticError:
            self.add_info(
                ast=first,
                tag=f"Member '{first}' defined here")

            self.add_info(
                ast=second,
                tag=f"Member '{second}' defined here")

            self.add_error(
                ast=field,
                tag=f"Ambiguous member access for '{field}'.",
                msg="The member access is ambiguous.",
                tip=f"Use 'std::upcast[T](...) to access ambiguous attributes of specific classes.")

            return self

    class TypeVoidInvalidUsageError(SemanticError):
        """
        The TypeVoidInvalidUsageError is raised if the void type is used in an invalid context. The void type cannot be
        used as a variable type, function return type, function parameter type etc.
        """

        def add(self, type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                ast=type,
                tag="Invalid use of void.",
                msg="The void type cannot be used in this context.",
                tip="Change the type to a valid type.")

            return self

    class TypeMismatchError(SemanticError):
        """
        The TypeMismatchError is raised if 2 types are different when they should not be. This could be in a variable
        assignment, function call, function return type etc.

        Todo: add potential alias's old type: (... aka: ...)
        """

        def add(
                self, existing_ast: Asts.Ast, existing_type: Asts.TypeAst, incoming_ast: Asts.Ast,
                incoming_type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=existing_ast,
                tag=f"Type inferred as '{existing_type}' here")

            self.add_error(
                ast=incoming_ast,
                tag=f"Type inferred as '{incoming_type}' here",
                msg="Type mismatch.",
                tip="Change the rhs type to match the lhs type.")

            return self

    class YieldedTypeMismatchError(SemanticError):
        """
        The YieldedTypeMismatchError is raised if 2 types are different when they should not be, in a yielding context.
        This is a separate error from TypeMismatchError, as it contains extra information about the yielding context.
        """

        def add(
                self, existing_ast: Asts.Ast, existing_type: Asts.TypeAst, incoming_ast: Asts.Ast,
                incoming_type: Asts.TypeAst, is_optional: bool, is_fallible: bool,
                error_type: Asts.TypeAst) -> SemanticError:

            self.add_info(
                ast=existing_ast,
                tag=f"Target yield type defined as '{existing_type}' here")

            if is_optional:
                self.add_info(
                    existing_ast,
                    tag=f"Yielded type is optional, so `gen` is valid.")

            if is_fallible:
                self.add_info(
                    existing_ast,
                    tag=f"Yielded type is fallible, so `gen {error_type}()` is valid.")

            self.add_error(
                ast=incoming_ast,
                tag=f"Type inferred as '{incoming_type}' here",
                msg="Type mismatch.",
                tip="Change the rhs type to match the lhs type.")

            return self

    class GenericParameterNotInferredError(SemanticError):
        """
        The GenericParameterNotInferredError is raised if a generic parameter is not inferred from its caller context.
        Inference comes from arguments.
        """

        def add(self, generic_parameter_name: Asts.TypeAst, caller_context: Asts.ExpressionAst) -> SemanticError:
            self.add_info(
                ast=caller_context,
                tag=f"Type '{caller_context}' created here")

            self.add_error(
                ast=generic_parameter_name,
                tag=f"Non-inferred generic parameter '{generic_parameter_name}'.",
                msg="Non-inferred generic parameters must be passed explicitly.",
                tip="Pass the missing generic argument into the call.")

            return self

    class GenericParameterInferredConflictInferredError(SemanticError):
        """
        The GenericParameterInferenceConflictError is raised if a generic parameter is inferred from multiple contexts,
        with different types. For example, "f[T](a: T, b: T)" called as "f(1, true)" would infer T as both BigInt and Bool.
        """

        def add(self, generic_parameter_name: Asts.TypeAst, inferred_1: Asts.Ast, inferred_2: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=inferred_1,
                tag=f"Generic inferred as '{inferred_1}' here")

            self.add_error(
                ast=inferred_2,
                tag=f"Generic inferred as '{inferred_2}' here",
                msg="Generic parameter inferred as multiple types.",
                tip="Ensure the generic parameter is inferred as a single type.")

            return self

    class GenericParameterInferredConflictExplicitError(SemanticError):
        """
        The GenericParameterInferencePassesExplicitlyError is raised if a generic parameter is inferred from its caller
        context, but is also passed explicitly. This is redundant and should be removed. For example, "f[T](a: T)" being
        called as "f[Bool](true)" contains the redundant explicit generic argument, even if the type is correct.
        """

        def add(self, generic_parameter_name: Asts.TypeAst, explicit: Asts.Ast, inferred: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=inferred,
                tag=f"Generic parameter {generic_parameter_name} inferred from here")

            self.add_error(
                ast=explicit,
                tag=f"Explicit generic argument '{explicit}'",
                msg="Explicit generic argument is redundant.",
                tip="Remove the explicit generic argument.")

            return self

    class GenericTypeInvalidUsageError(SemanticError):
        """
        The GenericTypeInvalidUsageError is raised if a generic type is used in an invalid context. An example would be
        trying to initialize a generic type.
        """

        def add(self, generic_value: Asts.Ast, generic_type: Asts.TypeAst, context: str) -> SemanticError:
            self.add_error(
                ast=generic_value,
                tag=f"Type inferred as '{generic_type}' (generic) here.",
                msg=f"Generic types cannot be used in a {context}.",
                tip=f"Change the generic type to a concrete type.")

            return self

    class ArrayElementsDifferentTypesError(SemanticError):
        """
        The ArrayElementsDifferentTypesError is raised if the elements of an array have different types. All elements in
        an array must have the same type.
        """

        def add(self, element_ast_1: Asts.ExpressionAst, element_type_1: Asts.TypeAst, element_ast_2: Asts.TypeAst, element_type_2: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=element_ast_1,
                tag=f"Element inferred as '{element_type_1}'")

            self.add_error(
                ast=element_ast_2,
                tag=f"Element inferred as '{element_type_2}'",
                msg="All elements in an array must have the same type.",
                tip="Change the element types to be the same.")

            return self

    class ArrayElementBorrowedError(SemanticError):
        """
        The ArrayElementBorrowedError is raised if an element in an array is borrowed. Array elements cannot be
        borrowed, and must all be owned.
        """

        def add(self, element: Asts.ExpressionAst, borrow_location: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=borrow_location,
                tag="Array element borrowed here")

            self.add_error(
                ast=element,
                tag="Array element borrowed.",
                msg="Array elements cannot be borrowed.",
                tip="Remove the borrow from the array element.")

            return self

    class MemoryInconsistentlyInitializedError(SemanticError):
        """
        The MemoryInconsistentlyInitializedError is raised if a memory symbol is inconsistently initialized in different
        branches of the code. This could be a move in one branch and not in another.
        """

        def add(
                self, ast: Asts.ExpressionAst, branch_1: Tuple[Asts.CaseExpressionBranchAst, bool],
                branch_2: Tuple[Asts.CaseExpressionBranchAst, bool], what: str) -> SemanticError:
            self.add_info(
                ast=branch_1[0],
                tag=f"Symbol '{ast}' {what} in this branch")

            self.add_info(
                ast=branch_2[0],
                tag=f"Symbol '{ast}' not {what} in this branch")

            self.add_error(
                ast=ast,
                tag="Inconsistently initialized symbol.",
                msg="Branches inconsistently initialize the symbol.",
                tip="Ensure the symbol is consistently initialized.")

            return self

    class MemoryInconsistentlyPinnedError(SemanticError):
        """
        The MemoryInconsistentlyPinnedError is raised if a memory symbol is inconsistently pinned in different branches
        of the code. This could be pinned in one branch and not in another.
        """

        def add(
                self, ast: Asts.ExpressionAst, branch_1: Tuple[Asts.CaseExpressionBranchAst, bool],
                branch_2: Tuple[Asts.CaseExpressionBranchAst, bool]) -> SemanticError:
            self.add_info(
                ast=branch_1[0],
                tag=f"Symbol '{ast}' {'pinned' if branch_1[1] else 'not pinned'} in this branch")

            self.add_info(
                ast=branch_2[0],
                tag=f"Symbol '{ast}' {'pinned' if branch_2[1] else 'not pinned'} in this branch")

            self.add_error(
                ast=ast,
                tag="Inconsistently pinned symbol.",
                msg="Branches inconsistently pin the symbol.",
                tip="Ensure the symbol is consistently pinned.")

            return self

    class MemoryNotInitializedUsageError(SemanticError):
        """
        The MemoryNotInitializedUsageError is raised if a memory symbol is used before it is initialized / after it has
        been moved.
        """

        def add(
                self, init_location: Asts.Ast, ast: Asts.ExpressionAst, move_location: Asts.Ast,
                sm: ScopeManager) -> SemanticError:

            if init_location:
                self.add_info(
                    ast=init_location,
                    tag=f"Symbol '{init_location}' initialized here")

            self.add_info(
                ast=move_location,
                tag=f"Symbol '{ast}' moved/uninitialized here")

            self.add_error(
                ast=ast,
                tag="Uninitialized memory used here.",
                msg="The memory has not been initialized or has been moved.",
                tip=f"Ensure the memory is initialized before use.")

            return self

    class MemoryPartiallyInitializedUsageError(SemanticError):
        """
        The MemoryPartiallyInitializedUsageError is raised if a memory symbol is used before it is fully initialized.
        Partially initialized objects have missing attributes.
        """

        def add(self, ast: Asts.ExpressionAst, partial_move_location: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=partial_move_location,
                tag=f"Symbol '{ast}' partially moved here")

            self.add_error(
                ast=ast,
                tag="Partially initialized memory used here.",
                msg="The memory has already been partially moved.",
                tip="Ensure the memory is fully initialized before use.")

            return self

    class MemoryMovedFromBorrowedContextError(SemanticError):
        """
        The MemoryMovedFromBorrowedContextError is raised if a memory symbol is moved from a borrowed context. This
        occurs when a attribute is moved of a &T type or a method consumes an attribute of the T type.
        """

        def add(self, move_location: Asts.Ast, borrow_location: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=borrow_location,
                tag="Symbol borrowed here")

            self.add_error(
                ast=move_location,
                tag="Moving from borrowed context.",
                msg="The memory is borrowed and cannot be moved.",
                tip="Remove the move operation.")

            return self

    class MemoryMovedWhilstLinkPinnedError(SemanticError):
        """
        The MemoryMovedWhilstLinkPinnedError is raised if a memory symbol is moved whilst it is pinned by another
        symbol. This occurs when for example a coroutine is moved, but is pinned by a borrow passed into it.
        """

        def add(self, move_location: Asts.Ast, symbol_initialization: Asts.Ast, pin_location: Asts.Ast, pin_initialization: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=pin_initialization,
                tag="Pinned borrow initialized here.")

            self.add_info(
                ast=symbol_initialization,
                tag="Pinned object defined here.")

            self.add_info(
                ast=pin_location,
                tag=f"Borrow here causes '{move_location}' to be pinned.")

            self.add_error(
                ast=move_location,
                tag=f"Extending lifetime of borrow '{pin_location}'.",
                msg="Cannot move a value into an outer scope that would extend a borrow lifetime.",
                tip="Remove the move operation.")

            return self

    class MemoryMovedWhilstPinnedError(SemanticError):
        """
        The MemoryMovedWhilstPinnedError is raised if a memory symbol is moved whilst it is pinned. This occurs when for
        example an owned object is moved, but is pinned as a borrow into a coroutine.
        """

        def add(self, move_location: Asts.Ast, symbol_initialization: Asts.Ast, pin_location: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=symbol_initialization,
                tag=f"Symbol '{symbol_initialization}' defined here.")

            self.add_info(
                ast=pin_location,
                tag=f"Symbol '{move_location}' pinned here as a borrow.")

            self.add_error(
                ast=move_location,
                tag=f"Moving pinned borrow '{pin_location}'.",
                msg="Cannot move a value that is pinned.",
                tip="Remove the move operation.")

            return self

    class MemoryOverlapUsageError(SemanticError):
        """
        The MemoryOverlapUsageError is raised if a memory symbol is used whilst it overlaps with another memory symbol.
        This occurs when in a function call such as "f(a.b, a.b.c)" where "a.b" and "a.b.c" overlap.
        """

        def add(self, overlap: Asts.Ast, ast: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=overlap,
                tag="Memory borrowed here.")

            self.add_error(
                ast=ast,
                tag="Memory overlap conflict.",
                msg="The memory overlap conflicts with another memory use.",
                tip="Remove the memory overlap conflict.")

            return self

    class MutabilityInvalidMutationError(SemanticError):
        """
        The MutabilityInvalidMutationError is raised if an immutable symbol is mutated. This occurs when a symbol is
        defined as immutable "let x = 4" and then mutated "x = 5".
        """

        def add(self, ast: Asts.ExpressionAst, move_location: Asts.Ast, immutable_definition: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=immutable_definition,
                tag="Symbol defined as immutable here")

            self.add_error(
                ast=move_location,
                tag="Attempting to mutate immutable symbol.",
                msg="The symbol is immutable and cannot be mutated.",
                tip="Change the symbol to be mutable.")

            return self

    class AssignmentInvalidLhsError(SemanticError):
        """
        The AssignmentInvalidLhsError is raised if the left-hand-side of an assignment is invalid. For example "1 = 2"
        would be an invalid assignment as the left-hand-side is a literal.
        """

        def add(self, lhs: Asts.Ast) -> SemanticError:
            self.add_error(
                ast=lhs,
                tag="Invalid assignment left-hand-side expression.",
                msg="The LHS of the assignment is invalid.",
                tip="Use a valid LHS for the assignment.")

            return self

    class AssignmentInvalidCompoundLhsError(SemanticError):
        """
        The AssignmentInvalidCompoundLhsError is raised if the left-hand-side of a compound assignment is invalid. For
        example "1 += 2" would be an invalid compound assignment as the left-hand-side is a literal.
        """

        def add(self, lhs: Asts.Ast) -> SemanticError:
            self.add_error(
                ast=lhs,
                tag="Invalid compound assignment left-hand-side expression.",
                msg="The LHS of the compound assignment is invalid.",
                tip="Use a valid LHS for the compound assignment.")

            return self

    class ExpressionTypeInvalidError(SemanticError):
        """
        The ExpressionTypeInvalidError is raised if an expression is of an invalid AST. For example, types can be used
        as the lhs of a postfix member access ("Type::static_method()"), but not as an argument for example "f(Type)".
        """

        def add(self, expression: Asts.ExpressionAst) -> SemanticError:
            self.add_error(
                ast=expression,
                tag="Invalid expression.",
                msg="The expression is not valid.",
                tip="Use a non-type and non-token expression.")

            return self

    class ExpressionNotBooleanError(SemanticError):
        """
        The ExpressionNotBooleanError is raised if an expression is not a boolean type when it is expected to be. This
        could be in a conditional statement, a loop condition etc.
        """

        def add(self, expression: Asts.ExpressionAst, type: Asts.TypeAst, what: str) -> SemanticError:
            self.add_error(
                ast=expression,
                tag=f"{what.capitalize()} expression inferred as '{type}'",
                msg=f"A {what} expression must be a boolean type.",
                tip="Change the expression to be a boolean type.")

            return self

    class ExpressionNotGeneratorError(SemanticError):
        """
        The ExpressionNotGeneratorError is raised if an expression is not a generator type when it is expected to be.
        This is when using "generator.next()" expressions.
        """

        def add(self, expression: Asts.ExpressionAst, type: Asts.TypeAst, what: str) -> SemanticError:
            self.add_error(
                ast=expression,
                tag=f"{what.capitalize()} expression inferred as '{type}'",
                msg=f"A {what} must be a generator type.",
                tip="Change the expression to be a generator type.")

            return self

    class MemberAccessStaticOperatorExpectedError(SemanticError):
        """
        The MemberAccessStaticOperatorExpectedError is raised if a static member access is expected, but a runtime
        member access is found. Static member access uses "::" and runtime member access uses ".".
        """

        def add(self, lhs: Asts.Ast, access_token: Asts.TokenAst) -> SemanticError:
            self.add_info(
                ast=lhs,
                tag="Static expression defined here")

            self.add_error(
                ast=access_token,
                tag="Runtime member access found.",
                msg="The member access operator '.' can only be used on runtime expressions.",
                tip="Use the member access operator '::' instead of '.'.")

            return self

    class MemberAccessRuntimeOperatorExpectedError(SemanticError):
        """
        The MemberAccessRuntimeOperatorExpectedError is raised if a runtime member access is expected, but a static
        member access is found. Static member access uses "::" and runtime member access uses ".".
        """

        def add(self, lhs: Asts.Ast, access_token: Asts.TokenAst) -> SemanticError:
            self.add_info(
                ast=lhs,
                tag="Runtime expression defined here")

            self.add_error(
                ast=access_token,
                tag="Static member access found.",
                msg="The member access operator '::' can only be used on static expressions.",
                tip="Use the member access operator '.' instead of '::'.")

            return self

    class MemberAccessNonIndexableError(SemanticError):
        """
        The MemberAccessNonIndexableError is raised if a member access is performed on a non-indexable type. For
        example, "let x = 5" followed by "x.4" would raise this error.
        """

        def add(self, lhs: Asts.Ast, lhs_type: Asts.TypeAst, access_token: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=lhs,
                tag=f"Type '{lhs_type}' inferred here")

            self.add_error(
                ast=access_token,
                tag="Member access on non-indexable type.",
                msg="The type does not support member access.",
                tip="Use a type that supports member access.")

            return self

    class MemberAccessIndexOutOfBoundsError(SemanticError):
        """
        The MemberAccessIndexOutOfBoundsError is raised if a member access is out of bounds for the type. For example,
        accessing the 4th element of a 3-tuple.
        """

        def add(self, lhs: Asts.Ast, lhs_type: Asts.TypeAst, number_token: Asts.TokenAst) -> SemanticError:
            self.add_info(
                ast=lhs,
                tag=f"Type '{lhs_type}' inferred here")

            self.add_error(
                ast=number_token,
                tag="Member access out of bounds.",
                msg="The member access is out of bounds.",
                tip="Use a valid member access.")

            return self

    class SuperimpositionGenericNamedArgumentError(SemanticError):
        """
        The SuperimpositionGenericNamedArgumentError is raised if a named argument is used in a superimposition.
        Superimpositions must match their class signature. For example, "sup [T, U] Point[T, U]" is fine, but
        "sup [A, B] Point[T=A, U=B]" is not.
        """

        def add(self, named_argument: Asts.GenericArgumentNamedAst) -> SemanticError:
            self.add_error(
                ast=named_argument,
                tag="Named argument in superimposition.",
                msg="Named arguments are not allowed in superimpositions.",
                tip="Remove the named argument or convert it to unnamed form. This will be relaxed in future versions.")

            return self

    class SuperimpositionGenericArgumentMismatchError(SemanticError):
        """
        The SuperimpositionGenericArgumentMismatchError is raised if a generic argument is mismatched in a
        superimposition. For the "cls Point[T, U]" type, the superimposition must look like "sup [T, U] Point[T, U]".
        """

        def add(self, generic_argument: Asts.GenericArgumentAst, superimposition: Asts.TokenAst) -> SemanticError:

            self.add_info(
                ast=superimposition,
                tag="Superimposition defined here")

            self.add_error(
                ast=generic_argument,
                tag=f"Generic argument mismatch with argument '{generic_argument}'.",
                msg="The superimposition generic argument does not match the class generic argument.",
                tip="Change the superimposition generic argument to match the class generic argument. This will be relaxed in future versions.")

            return self

    class SuperimpositionExtensionMethodInvalidError(SemanticError):
        """
        The SuperimpositionExtensionMethodInvalidError is raised if a subclass method does not exist on the superclass.
        The signature of the superclass method and subclass method must match exactly.
        """

        def add(self, new_method: Asts.IdentifierAst, super_class: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=super_class,
                tag=f"Super class '{super_class}' extended here")

            self.add_error(
                ast=new_method,
                tag="Invalid member.",
                msg="This member does not match any definitions on the superclass.",
                tip="Use a valid super member.")

            return self

    class SuperimpositionExtensionUseStatementInvalidError(SemanticError):
        """
        The SuperimpositionExtensionUseStatementInvalidError is raised if a subclass "use" statement does not exist on
        the superclass. Any associated type on an extension must belong to the superclass as-well.
        """

        def add(self, new_use_statement: Asts.TypeStatementAst, super_class: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=super_class,
                tag=f"Super class '{super_class}' extended here")

            self.add_error(
                ast=new_use_statement,
                tag="Invalid use statement.",
                msg=f"The associated type '{new_use_statement.new_type}' does not exist on the superclass.",
                tip="Move the associated type to an isolated 'sup' block.")

            return self

    class SuperimpositionExtensionCmpStatementInvalidError(SemanticError):
        """
        The SuperimpositionExtensionCmpStatementInvalidError is raised if a subclass "cmp" statement does not exist on
        the superclass. Any associated type on an extension must belong to the superclass as-well.
        """

        def add(self, new_cmp_statement: Asts.CmpStatementAst, super_class: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=super_class,
                tag=f"Super class '{super_class}' extended here")

            self.add_error(
                ast=new_cmp_statement,
                tag="Invalid use statement.",
                msg=f"The associated constant '{new_cmp_statement.name}' does not exist on the superclass.",
                tip="Move the associated type to an isolated 'sup' block.")

            return self

    class SuperimpositionExtensionNonVirtualMethodOverriddenError(SemanticError):
        """
        The SuperimpositionExtensionNonVirtualMethodOverriddenError is raised if a non-virtual method on the base
        class is overridden in the subclass. Non-virtual methods cannot be overridden.
        """

        def add(self, base_method: Asts.IdentifierAst, super_class: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=super_class,
                tag=f"Super class '{super_class}' extended here")

            self.add_error(
                ast=base_method,
                tag="Non-virtual method on base class.",
                msg=f"The super member '{base_method}' is not virtual and cannot be overridden in the subclass.",
                tip="Use a virtual method.")

            return self

    class SuperimpositionExtensionDuplicateSuperclassError(SemanticError):
        """
        The SuperimpositionExtensionDuplicateSuperclassError is raised if a type is superimposed twice over another
        type. The 2 matched types are symbolically equal, ie alias-aware, generically matched types.
        """

        def add(self, first_extension: Asts.TypeAst, second_extension: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=first_extension,
                tag=f"Type '{first_extension}' extended here")

            self.add_error(
                ast=second_extension,
                tag=f"Duplicate superimposition here",
                msg="Cannot superimpose the same type twice",
                tip="Remove the second superimposition definition")

            return self

    class SuperimpositionExtensionCyclicExtensionError(SemanticError):
        """
        The SuperimpositionExtensionCyclicSuperclassError is raised two types extend each other. Extension trees,
        whilst supporting multi-parents, must be loop free.
        """

        def add(self, first_extension: Asts.TypeAst, second_extension: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=first_extension,
                tag=f"Valid extension defined here")

            self.add_error(
                ast=second_extension,
                tag=f"Cyclic superimposition here",
                msg="Two types cannot superimpose each other",
                tip="Remove the second superimposition definition")

            return self

    class SuperimpositionExtensionSelfExtensionError(SemanticError):
        """
        The SuperimpositionExtensionSelfExtensionError is raised if a type extends itself. This is not allowed, as it
        would create an infinite loop in the extension tree.
        """

        def add(self, extension: Asts.TokenAst) -> SemanticError:
            self.add_error(
                ast=extension,
                tag="Self extension.",
                msg="A type cannot extend itself.",
                tip="Remove the self extension.")

            return self

    class SuperimpositionUnconstrainedGenericParameterError(SemanticError):
        """
        The SuperimpositionUnconstrainedGenericParameterError is raised if a generic parameter is unconstrained in a
        superimposition. All generic parameters must be constrained to the overridden type, as there is no way to pass a
        generic argument into a superimposition. Same as "non-inferrable" generic parameters.
        """

        def add(self, unconstrained_generic_parameter: Asts.GenericParameterAst, type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=type,
                tag="Type defined here")

            self.add_error(
                ast=unconstrained_generic_parameter,
                tag="Unconstrained generic parameter.",
                msg=f"The generic parameter '{unconstrained_generic_parameter}' is unconstrained.",
                tip="Remove the generic parameter.")

            return self

    class SuperimpositionOptionalGenericParameterError(SemanticError):
        """
        The SuperimpositionOptionalGenericParameterError is raised if a generic parameter is optional in a
        superimposition. As all generic parameters are inferrable in a superimposition, they cannot be optional.
        """

        def add(self, optional_generic_parameter: Asts.GenericParameterAst) -> SemanticError:
            self.add_error(
                ast=optional_generic_parameter,
                tag="Optional generic parameter.",
                msg=f"The generic parameter '{optional_generic_parameter}' is optional.",
                tip="Remove the optional generic parameter.")

            return self

    class LoopTooManyControlFlowStatementsError(SemanticError):
        """
        The LoopTooManyControlFlowStatementsError is raised if a loop has too many control flow statements. The maximum
        number of control flow statements is equal to the loop depth.
        """

        def add(
                self, loop: Asts.LoopExpressionAst, loop_control: Asts.LoopControlFlowStatementAst,
                number_of_controls: int, depth_of_loop: int) -> SemanticError:
            self.add_info(
                ast=loop,
                tag="Loop defined here")

            self.add_error(
                ast=loop_control,
                tag="Too many control flow statements.",
                msg=f"The loop has {number_of_controls} control flow statements, but the loop depth is only {depth_of_loop}.",
                tip="Remove some control flow statements from the loop.")

            return self

    class TupleElementBorrowedError(SemanticError):
        """
        The TupleElementBorrowedError is raised if an element in a tuple is borrowed. Array elements cannot be borrowed,
        and must all be owned.
        """

        def add(self, element: Asts.ExpressionAst, borrow_location: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=borrow_location,
                tag="Tuple element borrowed here")

            self.add_error(
                ast=element,
                tag="Tuple element borrowed.",
                msg="Tuple elements cannot be borrowed.",
                tip="Remove the borrow from the tuple element.")

            return self

    class CaseBranchesConflictingTypesError(SemanticError):
        """
        The CaseBranchesConflictingTypesError is raised if the branches in a case statement return conflicting types,
        and the case expression is being used for assignment.
        """

        def add(self, return_type_1: Asts.TypeAst, return_type_2: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=return_type_1,
                tag=f"Branch inferred as '{return_type_1}'")

            self.add_error(
                ast=return_type_2,
                tag=f"Branch inferred as '{return_type_2}'",
                msg="The branches return conflicting types.",
                tip="Ensure the branches return the same type.")

            return self

    class CaseBranchesMissingElseBranchError(SemanticError):
        """
        The CaseBranchesMissingElseBranchError is raised if a case statement is missing an else branch, and the case
        expression is being used for assignment.
        """

        def add(self, condition: Asts.ExpressionAst, final_branch: Asts.CaseExpressionBranchAst) -> SemanticError:
            self.add_info(
                ast=condition,
                tag="Case expression defined here")

            self.add_error(
                ast=final_branch,
                tag="Missing else branch.",
                msg="The case statement is missing an else branch.",
                tip="Add an else branch to the case statement.")

            return self

    class CaseBranchesElseBranchNotLastError(SemanticError):
        """
        The CaseBranchesElseBranchNotLastError is raised if the else branch is not the last branch in a case statement.
        """

        def add(self, else_branch: Asts.TokenAst, last_branch: Asts.CaseExpressionBranchAst) -> SemanticError:
            self.add_info(
                ast=else_branch,
                tag="Else branch defined here")

            self.add_error(
                ast=last_branch,
                tag="Branch defined after else branch.",
                msg="The else branch must be the last branch in the case statement.",
                tip="Move the else branch to the end of the case statement.")

            return self

    class CaseBranchMultipleDestructurePatternsError(SemanticError):
        """
        The CaseBranchMultipleDestructurePatternsError is raised if a case branch has multiple destructure patterns. A
        case branch can only have one destructure pattern.
        """

        def add(self, first_pattern: Asts.PatternVariantAst, second_pattern: Asts.PatternVariantAst) -> SemanticError:
            self.add_info(
                ast=first_pattern,
                tag="First destructure pattern defined here")

            self.add_error(
                ast=second_pattern,
                tag="Second destructure pattern defined here",
                msg="The case branch can only have one destructure pattern.",
                tip="Remove the second destructure pattern, or move it into another branch.")

            return self

    class VariableDestructureContainsMultipleMultiSkipsError(SemanticError):
        """
        The VariableDestructureContainsMultipleMultiSkipsError is raised if a variable destructure contains multiple
        multi-skips. A maximum of one multi-skip is allowed per destructure. The destructure "let (.., a, ..) = x" is
        invalid.
        """

        def add(
                self, first_multi_skip: Asts.LocalVariableDestructureSkipNArgumentsAst,
                second_multi_skip: Asts.LocalVariableDestructureSkipNArgumentsAst) -> SemanticError:
            self.add_info(
                ast=first_multi_skip,
                tag="First multi-skip defined here")

            self.add_error(
                ast=second_multi_skip,
                tag="Second multi-skip defined here.",
                msg="Only one multi-skip is allowed per destructure.",
                tip="Remove the one of the multi-skip tokens.")

            return self

    class VariableObjectDestructureWithBoundMultiSkipError(SemanticError):
        """
        The VariableObjectDestructureWithBoundMultiSkipError is raised if a variable object-destructure contains a
        multi-skip with a binding. For example, "let Point(x, y, ..) = p" is fine, but "let Point(..values) = p" is
        invalid.
        """

        def add(
                self, object_destructure: Asts.LocalVariableDestructureObjectAst,
                bound_multi_skip: Asts.LocalVariableDestructureSkipNArgumentsAst) -> SemanticError:
            self.add_info(
                ast=object_destructure,
                tag="Object destructure defined here")

            self.add_error(
                ast=bound_multi_skip,
                tag="Multi-skip with binding found.",
                msg="Multi-skip cannot contain a binding.",
                tip="Remove the binding from the multi-skip.")

            return self

    class VariableTupleDestructureTupleSizeMismatchError(SemanticError):
        """
        The VariableTupleDestructureTupleSizeMismatchError is raised if a variable tuple-destructure has a different
        number of elements than the tuple being destructured. For example, "let (a, b) = (1, 2, 3)" is invalid.
        """

        def add(
                self, lhs: Asts.LocalVariableDestructureTupleAst, lhs_count: int, rhs: Asts.Ast,
                rhs_count: int) -> SemanticError:
            self.add_info(
                ast=lhs,
                tag=f"{lhs_count}-tuple destructure defined here")

            self.add_error(
                ast=rhs,
                tag=f"Type inferred as a {rhs_count}-tuple here",
                msg="The tuple destructure has a different number of elements than the tuple being destructure.",
                tip="Change the tuple destructure to have the same number of elements as the tuple.")

            return self

    class VariableTupleDestructureTupleTypeMismatchError(SemanticError):
        """
        The VariableTupleDestructureTupleTypeMismatchError is raised if a tuple-destructure on a non-tuple type is
        attempted. It is a more specialized TypeMismatchError.
        """

        def add(
                self, destructure: Asts.LocalVariableDestructureTupleAst, rhs: Asts.ExpressionAst,
                rhs_type: Asts.TypeAst) -> SemanticError:

            self.add_info(
                ast=destructure,
                tag=f"Tuple destructure taking place here")

            self.add_error(
                ast=rhs,
                tag=f"Type inferred as '{rhs_type}' here",
                msg="The right hand side of a tuple destructure must be a tuple type.",
                tip="Change the right hand side expression")

            return self

    class VariableArrayDestructureArraySizeMismatchError(SemanticError):
        """
        The VariableArrayDestructureArraySizeMismatchError is raised if a variable array-destructure has a different
        number of elements than the array being destructured. For example, "let [a, b] = [1, 2, 3]" is invalid.
        """

        def add(
                self, lhs: Asts.LocalVariableDestructureArrayAst, lhs_count: int, rhs: Asts.Ast,
                rhs_count: int) -> SemanticError:

            self.add_info(
                ast=lhs,
                tag=f"{lhs_count}-array destructure defined here")

            self.add_error(
                ast=rhs,
                tag=f"Type inferred as a {rhs_count}-array here",
                msg="The array destructure has a different number of elements than the array being destructure.",
                tip="Change the array destructure to have the same number of elements as the array.")

            return self

    class VariableArrayDestructureArrayTypeMismatchError(SemanticError):
        """
        The VariableTupleDestructureArrayTypeMismatchError is raised if an array-destructure on a non-array type is
        attempted. It is a more specialized TypeMismatchError.
        """

        def add(
                self, destructure: Asts.LocalVariableDestructureArrayAst, rhs: Asts.ExpressionAst,
                rhs_type: Asts.TypeAst) -> SemanticError:

            self.add_info(
                ast=destructure,
                tag=f"Array destructure taking place here")

            self.add_error(
                ast=rhs,
                tag=f"Type of '{rhs}' inferred as '{rhs_type}' here",
                msg="The right hand side of an array destructure must be an array type.",
                tip="Change the right hand side expression")

            return self

    class AsyncFunctionCallInvalidTargetError(SemanticError):
        """
        The AsyncFunctionCallInvalidTargetError is raised if the target of an async function call is not a function. For
        example, whilst "async f()" is valid, "async 5" is not.
        """

        def add(self, async_modifier: Asts.Ast, target: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=async_modifier,
                tag="Async modifier used here")

            self.add_error(
                ast=target,
                tag="Invalid async function call target.",
                msg="The target of an async function call must be a function.",
                tip="Remove the async call modifier, or change the target to a function.")

            return self

    class ObjectInitializerMultipleDefArgumentsError(SemanticError):
        """
        The ObjectInitializerMultipleDefArgumentsError is raised if an object initializer has multiple default
        arguments. Only one default argument is allowed. For example, "Type(else=a, else=b)" is invalid".
        """

        def add(self, first_else: Asts.Ast, second_else: Asts.Ast) -> SemanticError:
            self.add_info(
                ast=first_else,
                tag="First default argument defined here")

            self.add_error(
                ast=second_else,
                tag="Second default argument defined here",
                msg="Only one default argument is allowed in an object initializer.",
                tip="Remove the second default argument.")

            return self

    class ObjectInitializerGenericWithArgumentsError(SemanticError):
        """
        An ObjectInitializerGenericWithArgumentsError error is raised if a generic type is being initialized (valid),
        but with arguments. This is invalid because generic types have different attributes. So only full default
        initialization can be used (no arguments).
        """

        def add(self, generic_type: Asts.TypeAst, argument: Asts.ObjectInitializerArgumentAst) -> SemanticError:
            self.add_info(
                ast=generic_type,
                tag=f"Generic type '{generic_type}' initialized here")

            self.add_error(
                ast=argument,
                tag="Argument defined here.",
                msg="Generic types cannot be initialized with arguments.",
                tip="Remove all arguments or use a concrete type.")

            return self

    class InvalidObjectInitializerArgumentError(SemanticError):
        """
        The InvalidObjectInitializerArgumentError is raised if an object initializer argument is unnamed and not an
        identifier. Without this error, the parser assumes a function call, which leads to weird errors if the lhs type
        is generic.
        """

        def add(self, argument: Asts.ExpressionAst) -> SemanticError:
            self.add_error(
                ast=argument,
                tag="Invalid object initializer argument unnamed here",
                msg="Unnamed argument must be identifiers",
                tip="Name the argument with an attribute identifier")

            return self

    class RecursiveTypeDefinitionError(SemanticError):
        """
        The RecursiveTypeDefinitionError is raised if a type definition is recursive. This is when a type definition
        refers to itself in its own definition, as an attribute, making the type an infinite size.
        """

        def add(self, class_prototype: Asts.ClassPrototypeAst, recursion_type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=class_prototype,
                tag="Type defined here")

            self.add_error(
                ast=recursion_type,
                tag="Recursive type definition.",
                msg="Cannot refer to the enclosing type within the definition of the type.",
                tip="Use Single[T] or Shared[T] instead.")

            return self

    class InvalidConventionLocationError(SemanticError):
        """
        The InvalidConventionLocationError is raised if a type has been declared with a convention, somewhere where a
        convention is not allowed. This includes attributes, return types etc.
        """

        def add(self, convention: Asts.ConventionAst, location: Asts.Ast, what: str) -> SemanticError:
            self.add_info(
                ast=convention,
                tag="Convention applied here")

            self.add_error(
                ast=location,
                tag="Invalid convention location.",
                msg=f"Conventions cannot be applied to {what}s.",
                tip="Remove the convention.")

            return self

    class InvalidSelfTypeError(SemanticError):
        """
        The InvalidSelfTypeError is raised if an arbitrary type passed to a self parameter does not superimpose the
        "Deref[Self]" type. This is because all "self" parameters must be either be "Self", with the inclusion of
        dereferencing to "Self".
        """

        def add(self, type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                ast=type,
                tag=f"Type inferred as '{type}'",
                msg="The type does not superimpose 'Deref[Self]'.",
                tip="Change the type to superimpose 'Deref[Self]'.")

            return self

    class InvalidTypeAnnotationError(SemanticError):
        """
        The InvalidTypeAnnotationError is raised if a type annotation is given to a "let" statement when the LHS isn't a
        single identifier. This is because in a destructuring context, giving a type isn't allowed as multiple types
        will be created from the symbols introduced.
        """

        def add(self, type: Asts.TypeAst, local_variable: Asts.LocalVariableAst) -> SemanticError:
            self.add_info(
                ast=local_variable,
                tag="Non-identifier local variable declared here")

            self.add_error(
                ast=type,
                tag="Type declared here",
                msg="A type cannot be given to a non-identifier 'let' statement",
                tip="Remove the type annotation")

            return self

    class UseStatementInvalidGenericArgumentsError(SemanticError):
        """
        The UseStatementInvalidGenericArgumentsError is raised is a "use" statement look lise "use std::vector[T]".
        Instead, it should just be "use std::vector" or "use vector[T] = std::vector[T]".
        """

        def add(self, use_statement: Asts.UseStatementAst, generic_argument: Asts.GenericArgumentAst) -> SemanticError:
            self.add_info(
                ast=use_statement,
                tag="Use statement defined here")

            self.add_error(
                ast=generic_argument,
                tag="Invalid generic argument in use statement.",
                msg="Generic arguments are not allowed in simple-alias use statements.",
                tip="Remove the generic argument from the use statement, or use the extended form.")

            return self

    class FunctionFoldTupleElementTypeMismatchError(SemanticError):
        """
        The FunctionFoldTupleElementTypeMismatchError is raised if a tuple being folded into a function has a different
        types in its elements. For example, "f((1, 2, 3)).." is valid, but "f((1, 2, "3")).." is invalid, because there
        are BigInt and Str elements in the tuple.
        """

        def add(self, first_type: Asts.TypeAst, mismatch: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=first_type,
                tag=f"Type inferred as '{first_type}' here")

            self.add_error(
                ast=mismatch,
                tag=f"Type inferred as '{mismatch}' here",
                msg="The tuple elements have different types.",
                tip="Ensure all tuple elements have the same type.")

            return self

    class FunctionFoldTupleLengthMismatchError(SemanticError):
        """
        The FunctionFoldTupleLengthMismatchError is raised if there are > 1 tuples being folded into a function call,
        and each tuple has a different number of elements.
        """

        def add(self, first_tuple: Asts.ExpressionAst, first_tuple_length: int, second_tuple: Asts.ExpressionAst, second_tuple_length: int) -> SemanticError:
            self.add_info(
                ast=first_tuple,
                tag=f"Tuple has {first_tuple_length} elements")

            self.add_error(
                ast=second_tuple,
                tag=f"Tuple has {second_tuple_length} elements",
                msg="The tuples have different lengths.",
                tip="Ensure all tuples have the same length.")

            return self

    class MissingMainFunctionError(SemanticError):
        """
        The MissingMainFunctionError is raised if the main function is missing from the program. The main function is
        the entry point and must match a certain signature.
        """

        def add(self, main_module: Asts.ModulePrototypeAst) -> SemanticError:
            self.add_error(
                ast=main_module,
                tag="Missing main function.",
                msg="The main function is missing from the program.",
                tip="Add a main function to the program.")
            return self

    class InvalidFfiSppTypeError(SemanticError):
        """
        The InvalidFfiSppTypeError is raised if a type is not a valid FFI type. This means it has to C ABI conversion,
        and therefore cannot be used for FFI.
        """

        def add(self, type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                ast=type,
                tag=f"Type inferred as '{type}'",
                msg="The type is not a valid FFI type.",
                tip="Change the type to a valid FFI type.")

            return self

    class InvalidFfiFunctionError(SemanticError):
        """
        The InvalidFfiFunctionError is raised if a function is not a valid FFI function. This means it has to C ABI
        conversion, and therefore cannot be used for FFI.
        """

        def add(self, function: Asts.IdentifierAst, dll: str) -> SemanticError:
            self.add_error(
                ast=function,
                tag=f"Sub function defined here.",
                msg=f"The function does not exist in the dll '{dll}'.",
                tip="Remove the invalid stub.")

            return self

    class IterExpressionBranchMissingError(SemanticError):
        """
        The IterExpressionBranchMissingError is raised if an iter expression block is missing a branch for a specific
        generator type, such as the "_" no-value branch got a GenOpt type.
        """

        def add(self, condition: Asts.ExpressionAst, generator_type: Asts.TypeAst, block: Asts.IterExpressionAst, missing_branch: type[Asts.IterPatternAst]) -> SemanticError:
            self.add_info(
                ast=condition,
                tag=f"Generator type '{generator_type}' inferred here")

            self.add_error(
                ast=block,
                tag=f"Iteration block missing a '{missing_branch.__name__}' branch.",
                msg=f"When inferring the type of an iter block, all cases must be considered.",
                tip=f"Add the missing block to the 'iter' expression.")

            return self

    class IterExpressionBranchTypeDuplicateError(SemanticError):
        """
        The IterExpressionBranchTypeDuplicateError is raised if an iter expression block has multiple branches with the
        same pattern type. For example, two branches with the same "IterPatternVariableAst" type.
        """

        def add(self, branch: Asts.IterExpressionBranchAst, duplicate_branch: Asts.IterExpressionBranchAst) -> SemanticError:
            self.add_info(
                ast=branch,
                tag="Branch defined here")

            self.add_error(
                ast=duplicate_branch,
                tag=f"Duplicate branch of type '{type(duplicate_branch.pattern)}' found.",
                msg="An iter expression block cannot have multiple branches with the same pattern type.",
                tip="Remove the duplicate branch.")

            return self

    class IterExpressionBranchIncompatibleError(SemanticError):
        """
        The IterExpressionBranchIncompatibleError is raised if an iter expression block has a branch that is
        incompatible with the condition type. For example, a branch with an "IterPatternNoValueAst" type
        when the condition is not a GenRes type.
        """

        def add(self, cond: Asts.ExpressionAst, cond_type: Asts.TypeAst, branch_pattern: Asts.IterPatternAst, expected_type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=cond,
                tag=f"Condition type '{cond_type}' inferred here")

            self.add_error(
                ast=branch_pattern,
                tag=f"Branch pattern incompatible with condition type '{cond_type}'.",
                msg="The branch pattern is not compatible with the condition type.",
                tip=f"Change the branch pattern to be compatible with the condition type '{expected_type}'.")

            return self

    class EarlyReturnRequiresTryTypeError(SemanticError):
        """
        The EarlyReturnRequiresTryTypeError is raised if an early return is used with an expression whose type doesn't
        superimpose the Try type. The Try type is needed to get the output argument (early return type).
        """

        def add(self, op: Asts.PostfixExpressionOperatorEarlyReturnAst, expr: Asts.ExpressionAst, expr_type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=op,
                tag="Early return operator used here")

            self.add_error(
                ast=expr,
                tag=f"Type inferred as '{expr_type}'",
                msg="The early return expression must superimpose the Try type.",
                tip="Change the expression type to superimpose the Try type.")

            return self

    class InvalidDereferenceExpressionConvention(SemanticError):
        """
        The InvalidDereferenceExpressionConvention error is raised if a dereference expression has an invalid expression
        convention; a dereference operation can only occur on borrow-convention types.
        """

        def add(self, deref_tok: Asts.UnaryExpressionOperatorDerefAst, rhs: Asts.ExpressionAst, rhs_type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=deref_tok,
                tag="Dereference expression defined here")

            self.add_error(
                ast=rhs,
                tag=f"Type inferred as '{rhs_type}'",
                msg="Dereference expressions can only occur on borrow-convention types.",
                tip="Change the expression type to a borrow-convention type, or remove the dereference operator.")

            return self

    class InvalidDereferenceExpressionType(SemanticError):
        """
        The InvalidDereferenceExpressionType error is raised if a dereference expression has an invalid type; a
        dereference operation can only occur on a type that superimposes "Copy".
        """

        def add(self, deref_tok: Asts.UnaryExpressionOperatorDerefAst, rhs: Asts.ExpressionAst, rhs_type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                ast=deref_tok,
                tag="Dereference expression defined here")

            self.add_error(
                ast=rhs,
                tag=f"Type inferred as '{rhs_type}'",
                msg="Dereference expressions can only occur on copyable types.",
                tip="Change the expression type to a copyable type.")

            return self
