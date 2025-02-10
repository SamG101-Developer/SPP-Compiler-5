from __future__ import annotations

from dataclasses import dataclass
from typing import List, NoReturn, Optional, Tuple, TYPE_CHECKING

from SParLex.Utils.ErrorFormatter import ErrorFormatter
from colorama import Fore, Style
from fastenum import Enum

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast


class SemanticError(BaseException):
    class Format(Enum):
        NORMAL = 0
        MINIMAL = 1
        NONE = 2

    @dataclass
    class ErrorInfo:
        pos: int
        tag: str
        msg: str
        tip: str
        fmt: SemanticError.Format

    error_info: List[ErrorInfo]

    def __init__(self, *args) -> None:
        super().__init__(args)
        self.error_info = []

    def add(self, *args, **kwargs) -> SemanticError:
        ...

    def add_error(self, pos: int, tag: str, msg: str, tip: str, fmt: Format = Format.NORMAL) -> SemanticError:
        # Add an error into the output list.
        self.error_info.append(SemanticError.ErrorInfo(pos, tag, msg, tip, fmt))
        return self

    def add_info(self, pos: int, tag: str) -> SemanticError:
        # Add an info message (minimal error metadata) into the output list.
        self.add_error(pos, tag, "", "", SemanticError.Format.MINIMAL)
        return self

    def _format_message(self, error_info: ErrorInfo) -> (str, bool):
        # For minimal formatting, the message remains empty, as a "tag" is provided.
        if error_info.fmt == SemanticError.Format.MINIMAL:
            return "", True

        # Otherwise, combine the message and tip into a single color-formatted string.
        f = f"\n{Style.BRIGHT}{type(self).__name__}: {Style.NORMAL}{error_info.msg}\n{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Tip: {Style.NORMAL}{error_info.tip}{Fore.RESET}"
        return f, False

    def throw(self, error_formatter: ErrorFormatter) -> NoReturn:
        # Format the error messages and raise the error.
        error_message = ""
        for error in self.error_info:
            formatted_message, is_minimal = self._format_message(error)
            error_message += error_formatter.error(error.pos, formatted_message, error.tag, is_minimal)
        print(error_message)
        raise type(self)()


class SemanticErrors:

    class AnnotationInvalidApplicationError(SemanticError):
        """
        The AnnotationInvalidApplicationError is raised if a standard annotation is applied to a non-compatible AST.
        This includes applying the "@public" annotation to a superimposition, or the "@no_impl" method annotation to a
        class. An allowlist of valid ASTs for the annotation is provided in the error message.
        """

        def add(self, annotation: Asts.IdentifierAst, applied_to: Ast, allow_list: str) -> SemanticError:
            self.add_info(
                pos=annotation.pos,
                tag=f"Annotation '{annotation}' defined here")

            self.add_error(
                pos=applied_to.pos,
                tag=f"Non-{allow_list} AST defined here.",
                msg=f"The '{annotation}' annotation can only be applied to {allow_list} ASTs.",
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
                pos=annotation.pos,
                tag="Invalid annotation.",
                msg=f"The annotation '{annotation}' is not a valid annotation.",
                tip=f"Remove the annotation from here.")

            return self

    class AnnotationDuplicateError(SemanticError):
        """
        The AnnotationDuplicateError is raised if the same annotation is applied multiple times to the same AST. Because
        the standard annotations modify ASTs before symbol generation, applying the same annotation twice is redundant
        and therefore not allowed.
        """

        def add(self, first_annotation: Asts.IdentifierAst, second_annotation: Asts.IdentifierAst) -> SemanticError:
            self.add_info(
                pos=first_annotation.pos,
                tag=f"Annotation '{first_annotation}' applied here")

            self.add_error(
                pos=second_annotation.pos,
                tag="Duplicate annotation.",
                msg=f"The annotation '{second_annotation}' is already applied.",
                tip=f"Remove the duplicate annotation.")

            return self

    class AnnotationConflictError(SemanticError):
        """
        The AnnotationConflictError is raised if there are 2 annotations on the same object that either have conflicting
        behaviour / are mutually exclusive. For example, using "@hot" and "@cold" on the same function would raise this
        error.
        """

        def add(self, first_annotation: Asts.IdentifierAst, conflicting_annotation: Asts.IdentifierAst) -> SemanticError:
            self.add_info(
                pos=first_annotation.pos,
                tag=f"Annotation '{first_annotation}' applied here")

            self.add_error(
                pos=conflicting_annotation.pos,
                tag="Conflicting annotation.",
                msg=f"The annotation '{conflicting_annotation}' conflicts with the first annotation.",
                tip=f"Remove the conflicting annotation.")

            return self

    class IdentifierDuplicationError(SemanticError):
        """
        The IdentifierDuplicationError is raised if the same identifier is defined multiple times in the same context.
        This could be for class attributes, function parameter names, generic parameter names etc.
        """

        def add(self, first_occurrence: Asts.IdentifierAst, second_occurrence: Asts.IdentifierAst, what: str) -> SemanticError:
            self.add_info(
                pos=first_occurrence.pos,
                tag=f"{what.capitalize()} '{first_occurrence}' defined here")

            self.add_error(
                pos=second_occurrence.pos,
                tag=f"Duplicate {what}.",
                msg=f"The {what} '{second_occurrence}' is already defined.",
                tip=f"Remove or rename the duplicate {what}.")

            return self

    class OrderInvalidError(SemanticError):
        """
        The OrderInvalidError is raised if a collection of ASTs is in the wrong order. This includes optional parameters
        before required parameters, or named arguments before unnamed arguments.
        """

        def add(self, first_what: str, first: Ast, second_what: str, second: Ast, what: str) -> SemanticError:
            self.add_info(
                pos=first.pos,
                tag=f"{first_what.capitalize()} {what} '{first}' defined here")

            self.add_error(
                pos=second.pos,
                tag=f"Invalid {what} order.",
                msg=f"The {second_what.lower()} {what} '{second}' is in the wrong position.",
                tip=f"Move the {second_what.lower()} {what} to after the {first_what.lower()} {what}.")

            return self

    class ParameterMultipleSelfError(SemanticError):
        """
        The ParameterMultipleSelfError is raised if there are multiple "self" parameters in a function definition. A
        maximum one "self" parameter is allowed per function.
        """

        def add(self, first_self_parameter: Asts.FunctionParameterAst, second_self_parameter: Asts.FunctionParameterAst) -> SemanticError:
            self.add_info(
                pos=first_self_parameter.pos,
                tag=f"Self parameter defined here")

            self.add_error(
                pos=second_self_parameter.pos,
                tag=f"Second 'self' parameter.",
                msg="Only one 'self' parameter is allowed.",
                tip="Remove the second 'self' parameter.")

            return self

    class ParameterMultipleVariadicError(SemanticError):
        """
        The ParameterMultipleVariadicError is raised if there are multiple variadic parameters in a function definition.
        A maximum one variadic parameter is allowed per function.
        """

        def add(self, first_variadic_parameter: Asts.FunctionParameterAst, second_variadic_parameter: Asts.FunctionParameterAst) -> SemanticError:
            self.add_info(
                pos=first_variadic_parameter.pos,
                tag=f"Variadic parameter '{first_variadic_parameter}' defined here")

            self.add_error(
                pos=second_variadic_parameter.pos,
                tag=f"Second variadic parameter '{second_variadic_parameter}.",
                msg="Only one variadic parameter is allowed.",
                tip="Remove the second variadic parameter.")

            return self

    class ParameterOptionalNonBorrowTypeError(SemanticError):
        """
        The ParameterOptionalNonBorrowTypeError is raised if an optional parameter has a borrow convention. Optional
        parameters cannot have borrow conventions, as borrows cannot be taken as part of an expression, only as a
        function argument. Therefore there is no way to give a default value that is a borrow.

        Todo: In the future, borrow conventions may be allowed as optional parameter expression prefixes.
        """

        def add(self, convention: Asts.ConventionAst) -> SemanticError:
            self.add_error(
                pos=convention.pos,
                tag="Borrow convention on optional parameter.",
                msg="Optional parameters cannot have borrow conventions.",
                tip="Change the convention to a move convention, or remove the default value.")

            return self

    class FunctionCoroutineInvalidReturnTypeError(SemanticError):
        """
        The FunctionCoroutineInvalidReturnTypeError is raised if a coroutine has a return type that is not a generator.
        All coroutines must return either GenMov, GenMut or GenRef (with optional generic type parameters).
        """

        def add(self, return_type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                pos=return_type.pos,
                tag="Invalid coroutine return type.",
                msg="The return type of a coroutine must be a generator.",
                tip="Change the return type to one of 'GenMov', 'GenMut' or 'GenRef'.")

            return self

    class FunctionCoroutineContainsReturnStatementError(SemanticError):
        """
        The FunctionCoroutineContainsRetError is raised if a coroutine contains a return statement. Coroutines cannot
        contain "ret" statements, only "gen" expressions, which yield a value. The actual generator is implicitly
        returned as soon as the function is called.
        """

        def add(self, coroutine_definition: Asts.TokenAst, return_statement: Asts.TokenAst) -> SemanticError:
            self.add_info(
                pos=coroutine_definition.pos,
                tag="Coroutine defined here")

            self.add_error(
                pos=return_statement.pos,
                tag="Return statement in coroutine.",
                msg="Coroutines cannot contain return statements.",
                tip="Remove the return statement.")

            return self

    class FunctionSubroutineContainsGenExpressionError(SemanticError):
        """
        The FunctionSubroutineContainsGenError is raised if a subroutine contains a "gen" expression. Subroutines cannot
        contain "gen" expressions, only "ret" statements, which return a value.
        """

        def add(self, subroutine_definition: Asts.TokenAst, gen_expression: Asts.TokenAst) -> SemanticError:
            self.add_info(
                pos=subroutine_definition.pos,
                tag="Subroutine defined here")

            self.add_error(
                pos=gen_expression.pos,
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
                pos=final_member.pos,
                tag="Non-ret statement found here")

            self.add_error(
                pos=return_type.pos,
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

        def add(self, first_prototype: Asts. IdentifierAst, second_prototype: Asts.IdentifierAst) -> SemanticError:
            self.add_info(
                pos=first_prototype.pos,
                tag="First prototype defined here")

            self.add_error(
                pos=second_prototype.pos,
                tag="Duplicate prototype.",
                msg="The function prototype is a duplicate of another prototype.",
                tip="Remove the duplicate prototype.")

            return self

    class ArgumentNameInvalidError(SemanticError):
        """
        The ArgumentNameInvalidError is raised if a named argument has been provided with a name that is not valid based
        on the target. This would be parameter vs argument name or attribute vs object initialization argument name. The
        source is the parameter/attribute, and the target is the argument.
        """

        def add(self, target: Ast, what_target: str, source: Ast, what_source: str) -> SemanticError:
            self.add_info(
                pos=target.pos,
                tag=f"{what_target.capitalize()} '{target}' defined here")

            self.add_error(
                pos=source.pos,
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

        def add(self, where: Ast, target: Ast, what_target: str, what_source: str) -> SemanticError:
            self.add_info(
                pos=target.pos,
                tag=f"{what_target.capitalize()} defined here")

            self.add_error(
                pos=where.pos,
                tag=f"Missing {what_source} name.",
                msg=f"Missing the {what_source} '{target}'.",
                tip=f"Add the missing {what_target} name.")

            return self

    class ArgumentTupleExpansionOfNonTupleError(SemanticError):
        """
        The ArgumentTupleExpansionOfNonTupleError is raised if a tuple expansion is used on a non-tuple type. Tuple
        expansions can only be used on tuples, such as "f(..tuple_argument)".
        """

        def add(self, expansion_arg: Ast, arg_type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                pos=expansion_arg.pos,
                tag=f"Type inferred as '{arg_type}' here",
                msg="Tuple expansions can only be used on tuples.",
                tip="Remove the '..' from the argument.")

            return self

    class FunctionCallNoValidSignaturesError(SemanticError):
        """
        The FunctionCallNoValidSignaturesError is raised if a function call has no valid signatures that match the
        arguments provided. A list of valid signatures is provided in the error message.
        """

        def add(self, function_call: Ast, signatures: str, attempted: str) -> SemanticError:
            self.add_error(
                pos=function_call.pos,
                tag="Invalid arguments for function call",
                msg="There are no overloads accepting the given arguments",
                tip=f"\n\t{signatures.replace("\n", "\n\t")}\n\nAttempted signature:\n\t{attempted}")

            return self

    class FunctionCallAmbiguousSignaturesError(SemanticError):
        """
        The FunctionCallAmbiguousSignaturesError is raised if a function call has multiple valid signatures that match
        the arguments provided. This is caused by generic substitution causing a match with multiple overloads. Concrete
        types signature conflicts are detected on function prototype analysis.
        """

        def add(self, function_call: Ast, signatures: str, attempted: str) -> SemanticError:
            self.add_error(
                pos=function_call.pos,
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

        def add(self, function: Asts.IdentifierAst, function_call: Asts.PostfixExpressionOperatorFunctionCallAst) -> SemanticError:
            self.add_info(
                pos=function.pos,
                tag="Function annotated as abstract")

            self.add_error(
                pos=function_call.pos,
                tag="Abstract method called here.",
                msg="Cannot call abstract methods.",
                tip="Call the method on a subtype")

            return self

    class FunctionCallOnNoncallableTypeError(SemanticError):
        """
        The FunctionCallOnNoncallableTypeError is raised if a non-callable type is called as a function. This could be a
        literal like "5()".
        """

        def add(self, function_call: Asts.ExpressionAst) -> SemanticError:
            self.add_error(
                pos=function_call.pos,
                tag="Non-callable inferred here.",
                msg="The type is not callable.",
                tip="Change the type to a callable type.")

            return self
            
    class FunctionCallTooManyArgumentsError(SemanticError):
        """
        The FunctionCallTooManyArgumentsError is raised if a function call has too many arguments.
        Todo: add more info?
        """

        def add(self, function_call: Asts.ExpressionAst, function_definition: Asts.IdentifierAst) -> SemanticError:
            self.add_info(
                pos=function_definition.pos,
                tag="Function defined here")

            self.add_error(
                pos=function_call.pos,
                tag="Too many arguments.",
                msg="The function call has too many arguments.",
                tip="Remove the extra arguments.")

            return self

    class UnreachableCodeError(SemanticError):
        """
        The UnreachableCodeError is raised if there is code after a skip/exit/ret keyword in the same scope. This code
        is unreachable as the keyword always exits the scope into the parent scope.
        """

        def add(self, return_ast: Asts.RetStatementAst, next_ast: Ast) -> SemanticError:
            self.add_info(
                pos=return_ast.pos,
                tag="Return statement defined here")

            self.add_error(
                pos=next_ast.pos,
                tag="Unreachable code.",
                msg="The code after the return statement is unreachable.",
                tip="Remove the unreachable code or move the return statement.")

            return self

    class NumberOutOfBoundsError(SemanticError):
        """
        The NumberOutOfBoundsError is raised if a number is out of the valid range for the type. This includes integer
        literals that are too large or too small, and float literals that are too large or too small.
        """

        def add(self, number: Asts.IntegerLiteralAst | Asts.FloatLiteralAst, minimum: int, maximum: int, what: str) -> SemanticError:
            self.add_error(
                pos=number.pos,
                tag=f"{what.capitalize()} out of range.",
                msg=f"The {what} '{number}' is out of range [{minimum}, {maximum}].",
                tip=f"Change the number to be within the range, or change the type specifier.")

            return self

    class IdentifierUnknownError(SemanticError):
        """
        The IdentifierUnknownError is raised if an identifier is used that is not defined in the current scope. This
        could be a variable, attribute, namespace, type etc.
        """

        def add(self, identifier: Asts.IdentifierAst | Asts.GenericIdentifierAst, what: str, closest_match: Optional[str]) -> SemanticError:
            self.add_error(
                pos=identifier.pos,
                tag=f"Undefined {what}: '{identifier}'.",
                msg=f"The {what} '{identifier}' is not defined.",
                tip=f"Did you mean '{closest_match}'?" if closest_match else f"Define the {what}.")

            return self

    class TypeVoidInvalidUsageError(SemanticError):
        """
        The TypeVoidInvalidUsageError is raised if the void type is used in an invalid context. The void type cannot be
        used as a variable type, function return type, function parameter type etc.
        """

        def add(self, type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                pos=type.pos,
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

        def add(self, existing_ast: Ast, existing_type: InferredType, incoming_ast: Ast, incoming_type: InferredType) -> SemanticError:
            self.add_info(
                pos=existing_ast.pos,
                tag=f"Type inferred as '{existing_type}' here")

            self.add_error(
                pos=incoming_ast.pos,
                tag=f"Type inferred as '{incoming_type}' here",
                msg="Type mismatch.",
                tip="Change the rhs type to match the lhs type.")

            return self

    class GenericParameterNotInferredError(SemanticError):
        """
        The GenericParameterNotInferredError is raised if a generic parameter is not inferred from its caller context.
        Inference comes from arguments.
        """

        def add(self, generic_parameter: Asts.GenericParameterAst, caller_context: Asts.ExpressionAst) -> SemanticError:
            self.add_info(
                pos=caller_context.pos,
                tag="Type created here")

            self.add_error(
                pos=generic_parameter.pos,
                tag="Non-inferred generic parameter.",
                msg="Non-inferred generic parameters must be passed explicitly.",
                tip="Pass the missing generic argument into the call.")

            return self

    class GenericParameterInferredConflictInferredError(SemanticError):
        """
        The GenericParameterInferenceConflictError is raised if a generic parameter is inferred from multiple contexts,
        with different types. For example, "f[T](a: T, b: T)" called as "f(1, true)" would infer T as both BigInt and Bool.
        """
            
        def add(self, generic_parameter: Asts.GenericParameterAst, inferred_1: Ast, inferred_2: Ast) -> SemanticError:
            self.add_info(
                pos=inferred_1.pos,
                tag=f"Generic inferred as '{inferred_1}' here")

            self.add_error(
                pos=inferred_2.pos,
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

        def add(self, generic_parameter: Asts.GenericParameterAst, explicit: Ast, inferred: Ast) -> SemanticError:
            self.add_info(
                pos=inferred.pos,
                tag=f"Generic parameter {generic_parameter} inferred from here")

            self.add_error(
                pos=explicit.pos,
                tag=f"Explicit generic argument '{explicit}'",
                msg="Explicit generic argument is redundant.",
                tip="Remove the explicit generic argument.")

            return self

    class GenericTypeInvalidUsageError(SemanticError):
        """
        The GenericTypeInvalidUsageError is raised if a generic type is used in an invalid context. An example would be
        trying to initialize a generic type.
        """

        def add(self, generic_value: Ast, generic_type: Asts.TypeAst, context: str) -> SemanticError:
            self.add_error(
                pos=generic_value.pos,
                tag=f"Type inferred as '{generic_type}' (generic) here.",
                msg=f"Generic types cannot be used in a {context}.",
                tip=f"Change the generic type to a concrete type.")

            return self

    class ArrayElementsDifferentTypesError(SemanticError):
        """
        The ArrayElementsDifferentTypesError is raised if the elements of an array have different types. All elements in
        an array must have the same type.
        """

        def add(self, element_type_1: Asts.TypeAst, element_type_2: Asts.TypeAst) -> SemanticError:
            self.add_info(
                pos=element_type_1.pos,
                tag=f"Element inferred as '{element_type_1}'")

            self.add_error(
                pos=element_type_2.pos,
                tag=f"Element inferred as '{element_type_2}'",
                msg="All elements in an array must have the same type.",
                tip="Change the element types to be the same.")

            return self

    class ArrayElementBorrowedError(SemanticError):
        """
        The ArrayElementBorrowedError is raised if an element in an array is borrowed. Array elements cannot be
        borrowed, and must all be owned.
        """

        def add(self, element: Asts.ExpressionAst, borrow_location: Ast) -> SemanticError:
            self.add_info(
                pos=borrow_location.pos,
                tag="Array element borrowed here")

            self.add_error(
                pos=element.pos,
                tag="Array element borrowed.",
                msg="Array elements cannot be borrowed.",
                tip="Remove the borrow from the array element.")

            return self

    class MemoryInconsistentlyInitializedError(SemanticError):
        """
        The MemoryInconsistentlyInitializedError is raised if a memory symbol is inconsistently initialized in different
        branches of the code. This could be a move in one branch and not in another.
        """

        def add(self, ast: Asts.ExpressionAst, branch_1: Tuple[Asts.CaseExpressionBranchAst, bool], branch_2: Tuple[Asts.CaseExpressionBranchAst, bool], what: str) -> SemanticError:
            self.add_info(
                pos=branch_1[0].pos,
                tag=f"Symbol '{ast}' {what} in this branch")

            self.add_info(
                pos=branch_2[0].pos,
                tag=f"Symbol '{ast}' not {what} in this branch")

            self.add_error(
                pos=ast.pos,
                tag="Inconsistently initialized symbol.",
                msg="Branches inconsistently initialize the symbol.",
                tip="Ensure the symbol is consistently initialized.")

            return self

    class MemoryInconsistentlyPinnedError(SemanticError):
        """
        The MemoryInconsistentlyPinnedError is raised if a memory symbol is inconsistently pinned in different branches
        of the code. This could be pinned in one branch and not in another.
        """

        def add(self, ast: Asts.ExpressionAst, branch_1: Tuple[Asts.CaseExpressionBranchAst, bool], branch_2: Tuple[Asts.CaseExpressionBranchAst, bool]) -> SemanticError:
            self.add_info(
                pos=branch_1[0].pos,
                tag=f"Symbol '{ast}' {'pinned' if branch_1[1] else 'not pinned'} in this branch")

            self.add_info(
                pos=branch_2[0].pos,
                tag=f"Symbol '{ast}' {'pinned' if branch_2[1] else 'not pinned'} in this branch")

            self.add_error(
                pos=ast.pos,
                tag="Inconsistently pinned symbol.",
                msg="Branches inconsistently pin the symbol.",
                tip="Ensure the symbol is consistently pinned.")

            return self

    class MemoryNotInitializedUsageError(SemanticError):
        """
        The MemoryNotInitializedUsageError is raised if a memory symbol is used before it is initialized / after it has
        been moved.
        """

        def add(self, ast: Asts.ExpressionAst, move_location: Ast) -> SemanticError:
            self.add_info(
                pos=move_location.pos,
                tag=f"Symbol '{ast}' moved/uninitialized here")

            self.add_error(
                pos=ast.pos,
                tag="Uninitialized memory used here.",
                msg="The memory has not been initialized or has been moved.",
                tip="Ensure the memory is initialized before use.")

            return self

    class MemoryPartiallyInitializedUsageError(SemanticError):
        """
        The MemoryPartiallyInitializedUsageError is raised if a memory symbol is used before it is fully initialized.
        Partially initialized objects have missing attributes.
        """

        def add(self, ast: Asts.ExpressionAst, partial_move_location: Ast) -> SemanticError:
            self.add_info(
                pos=partial_move_location.pos,
                tag=f"Symbol '{ast}' partially moved here")

            self.add_error(
                pos=ast.pos,
                tag="Partially initialized memory used here.",
                msg="The memory has already been partially moved.",
                tip="Ensure the memory is fully initialized before use.")

            return self

    class MemoryMovedFromBorrowedContextError(SemanticError):
        """
        The MemoryMovedFromBorrowedContextError is raised if a memory symbol is moved from a borrowed context. This
        occurs when a attribute is moved of a &T type or a method consumes an attribute of the T type.
        """

        def add(self, move_location: Ast, borrow_location: Ast) -> SemanticError:
            self.add_info(
                pos=borrow_location.pos,
                tag="Symbol borrowed here")

            self.add_error(
                pos=move_location.pos,
                tag="Moving from borrowed context.",
                msg="The memory is borrowed and cannot be moved.",
                tip="Remove the move operation.")

            return self

    class MemoryMovedWhilstPinnedError(SemanticError):
        """
        The MemoryMovedWhilstPinnedError is raised if a memory symbol is moved whilst it is pinned. This occurs when a
        pinned memory is moved.
        """

        def add(self, move_location: Ast, pin_location: Ast) -> SemanticError:
            self.add_info(
                pos=pin_location.pos,
                tag="Symbol pinned here")

            self.add_error(
                pos=move_location.pos,
                tag="Moving pinned memory.",
                msg="The memory is pinned and cannot be moved.",
                tip="Remove the move operation.")

            return self

    class MemoryOverlapUsageError(SemanticError):
        """
        The MemoryOverlapUsageError is raised if a memory symbol is used whilst it overlaps with another memory symbol.
        This occurs when in a function call such as "f(a.b, a.b.c)" where "a.b" and "a.b.c" overlap.
        """

        def add(self, overlap: Ast, ast: Ast) -> SemanticError:
            self.add_info(
                pos=overlap.pos,
                tag="Memory overlap defined here")

            self.add_error(
                pos=ast.pos,
                tag="Memory overlap conflict.",
                msg="The memory overlap conflicts with another memory use.",
                tip="Remove the memory overlap conflict.")

            return self

    class MemoryUsageOfUnpinnedBorrowError(SemanticError):
        """
        The MemoryUsageOfUnpinnedBorrowError is raised if a memory symbol is used whilst it is an unpinned
        borrow. This occurs when a borrow is used without being pinned.
        """

        def add(self, ast: Ast, pinned_required_ast: Ast) -> SemanticError:
            self.add_info(
                pos=pinned_required_ast.pos,
                tag="Context declared where pins are required.")

            self.add_error(
                pos=ast.pos,
                tag="Unpinned borrow used.",
                msg="Borrow must be pinned for use in this.",
                tip="Pin the borrow.")

            return self

    class MemoryPinTargetInvalidError(SemanticError):
        """
        The MemoryPinTargetInvalidError is raised if a memory symbol is pinned to an invalid target. This occurs when a
        non-symbolic value, ie "1" is used as the pin target.
        """

        def add(self, pin_rel_statement: Asts.PinStatementAst | Asts.RelStatementAst, pin_target: Ast, pin: bool) -> SemanticError:
            self.add_info(
                pos=pin_rel_statement.pos,
                tag=f"{"Pin" if pin else "Rel"} statement defined here")

            self.add_error(
                pos=pin_target.pos,
                tag="Invalid pin target.",
                msg="The pin target must be a symbolic.",
                tip="Change the pin target to a symbolic value.")

            return self
            
    class MemoryPinOverlapError(SemanticError):
        """
        The MemoryPinOverlapError is raised if 2 memory pins overlap. For example, "pin a" and "pin a.b" would overlap,
        and therefore raise this error.
        """
        
        def add(self, pin_1: Ast, pin_2: Ast) -> SemanticError:
            self.add_info(
                pos=pin_1.pos,
                tag="Pin target pinned here")

            self.add_error(
                pos=pin_2.pos,
                tag="Second pin target pinned here",
                msg="Memory pins overlap.",
                tip="Remove the more refined pin target.")

            return self

    class MemoryReleasingNonPinnedSymbolError(SemanticError):
        """
        The MemoryReleasingNonPinnedSymbolError is raised if a memory symbol is released without being pinned.
        """

        def add(self, rel_statement: Asts.RelStatementAst, release_target: Ast) -> SemanticError:
            self.add_info(
                pos=rel_statement.pos,
                tag="Release statement defined here")

            self.add_error(
                pos=release_target.pos,
                tag="Non-pinned memory released.",
                msg="Memory must be pinned before being released.",
                tip="Remove the rel target.")

            return self

    class MemoryReleasingConstantSymbolError(SemanticError):
        """
        The MemoryReleasingConstantSymbolError is raised if a constant memory symbol is released. Constants cannot be
        released as they must be statically pinned (ie permanently pinned).
        """

        def add(self, rel_statement: Asts.RelStatementAst, release_target: Ast, target_initialization_ast: Ast) -> SemanticError:
            self.add_info(
                pos=rel_statement.pos,
                tag="Release statement defined here")

            self.add_info(
                pos=target_initialization_ast.pos,
                tag="Constant memory defined here")

            self.add_error(
                pos=release_target.pos,
                tag="Constant memory released.",
                msg="Constants cannot be released.",
                tip="Remove the rel target.")

            return self

    class MutabilityInvalidMutationError(SemanticError):
        """
        The MutabilityInvalidMutationError is raised if an immutable symbol is mutated. This occurs when a symbol is
        defined as immutable "let x = 4" and then mutated "x = 5".
        """

        def add(self, ast: Asts.ExpressionAst, move_location: Ast, immutable_definition: Ast) -> SemanticError:
            self.add_info(
                pos=immutable_definition.pos,
                tag="Symbol defined as immutable here")

            self.add_error(
                pos=move_location.pos,
                tag="Attempting to mutate immutable symbol.",
                msg="The symbol is immutable and cannot be mutated.",
                tip="Change the symbol to be mutable.")

            return self

    class AssignmentInvalidLhsError(SemanticError):
        """
        The AssignmentInvalidLhsError is raised if the left-hand-side of an assignment is invalid. For example "1 = 2"
        would be an invalid assignment as the left-hand-side is a literal.
        """

        def add(self, lhs: Ast) -> SemanticError:
            self.add_error(
                pos=lhs.pos,
                tag="Invalid assignment left-hand-side expression.",
                msg="The LHS of the assignment is invalid.",
                tip="Use a valid LHS for the assignment.")

            return self

    class AssignmentInvalidCompoundLhsError(SemanticError):
        """
        The AssignmentInvalidCompoundLhsError is raised if the left-hand-side of a compound assignment is invalid. For
        example "1 += 2" would be an invalid compound assignment as the left-hand-side is a literal.
        """

        def add(self, lhs: Ast) -> SemanticError:
            self.add_error(
                pos=lhs.pos,
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
                pos=expression.pos,
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
                pos=expression.pos,
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
                pos=expression.pos,
                tag=f"{what.capitalize()} expression inferred as '{type}'",
                msg=f"A {what} expression must be a generator type.",
                tip="Change the expression to be a generator type.")

            return self

    class MemberAccessStaticOperatorExpectedError(SemanticError):
        """
        The MemberAccessStaticOperatorExpectedError is raised if a static member access is expected, but a runtime
        member access is found. Static member access uses "::" and runtime member access uses ".".
        """

        def add(self, lhs: Ast, access_token: Asts.TokenAst) -> SemanticError:
            self.add_info(
                pos=lhs.pos,
                tag="Static expression defined here")

            self.add_error(
                pos=access_token.pos,
                tag="Runtime member access found.",
                msg="The member access operator '.' can only be used on runtime expressions.",
                tip="Use the member access operator '::' instead of '.'.")

            return self

    class MemberAccessRuntimeOperatorExpectedError(SemanticError):
        """
        The MemberAccessRuntimeOperatorExpectedError is raised if a runtime member access is expected, but a static
        member access is found. Static member access uses "::" and runtime member access uses ".".
        """

        def add(self, lhs: Ast, access_token: Asts.TokenAst) -> SemanticError:
            self.add_info(
                pos=lhs.pos,
                tag="Runtime expression defined here")

            self.add_error(
                pos=access_token.pos,
                tag="Static member access found.",
                msg="The member access operator '::' can only be used on static expressions.",
                tip="Use the member access operator '.' instead of '::'.")

            return self

    class MemberAccessAmbiguousError(SemanticError):
        """
        The MemberAccessAmbiguousError is raised if a member access is ambiguous. This occurs when there are multiple
        possible member accesses for the same expression.
        """

        def add(self, member: Asts.IdentifierAst, scopes: Seq[Asts.IdentifierAst]) -> SemanticError:
            self.add_error(
                pos=member.pos,
                tag=f"Ambiguous member access: {scopes.join(", ")}",
                msg="The member access is ambiguous.",
                tip="Use 'std::upcast[T](...)' to select the base class.")

            return self

    class MemberAccessNonIndexableError(SemanticError):
        """
        The MemberAccessNonIndexableError is raised if a member access is performed on a non-indexable type. For
        example, "let x = 5" followed by "x.4" would raise this error.
        """

        def add(self, lhs: Ast, lhs_type: Asts.TypeAst, access_token: Asts.TokenAst) -> SemanticError:
            self.add_info(
                pos=lhs.pos,
                tag=f"Type '{lhs_type}' inferred here")

            self.add_error(
                pos=access_token.pos,
                tag="Member access on non-indexable type.",
                msg="The type does not support member access.",
                tip="Use a type that supports member access.")

            return self

    class MemberAccessIndexOutOfBoundsError(SemanticError):
        """
        The MemberAccessIndexOutOfBoundsError is raised if a member access is out of bounds for the type. For example,
        accessing the 4th element of a 3-tuple.
        """

        def add(self, lhs: Ast, lhs_type: Asts.TypeAst, number_token: Asts.TokenAst) -> SemanticError:
            self.add_info(
                pos=lhs.pos,
                tag=f"Type '{lhs_type}' inferred here")

            self.add_error(
                pos=number_token.pos,
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
                pos=named_argument.pos,
                tag="Named argument in superimposition.",
                msg="Named arguments are not allowed in superimpositions.",
                tip="Remove the named argument or convert it to unnamed form. This will be relaxed in future versions.")

            return self

    class SuperimpositionGenericArgumentMismatchError(SemanticError):
        """
        The SuperimpositionGenericArgumentMismatchError is raised if a generic argument is mismatched in a
        superimposition. For the "cls Point[T, U]" type, the superimposition must look like "sup [T, U] Point[T, U]".
        """

        def add(self, generic_argument: Asts.GenericArgumentAst, superimposition: Asts.SupPrototypeAst) -> SemanticError:
            self.add_info(
                pos=superimposition.pos,
                tag="Superimposition defined here")

            self.add_error(
                pos=generic_argument.pos,
                tag="Generic argument mismatch.",
                msg="The superimposition generic argument does not match the class generic argument.",
                tip="Change the superimposition generic argument to match the class generic argument. This will be relaxed in future versions.")

            return self

    class SuperimpositionInheritanceMethodInvalidError(SemanticError):
        """
        The SuperimpositionInheritanceMethodInvalidError is raised if a subclass method does not exist on the
        superclass. The signature of the superclass method and subclass method must match exactly.
        """

        def add(self, new_method: Asts.IdentifierAst, super_class: Asts.TypeAst) -> SemanticError:
            self.add_info(
                pos=super_class.pos,
                tag=f"Super class '{super_class}' extended here")

            self.add_error(
                pos=new_method.pos,
                tag="Invalid member.",
                msg=f"The subclass member '{new_method}' does not exist in the superclass '{super_class}'.",
                tip="Use a valid super member.")

            return self

    class SuperimpositionInheritanceNonVirtualMethodOverriddenError(SemanticError):
        """
        The SuperimpositionInheritanceNonVirtualMethodOverriddenError is raised if a non-virtual method on the base
        class is overridden in the subclass. Non-virtual methods cannot be overridden.
        """

        def add(self, base_method: Asts.IdentifierAst, super_class: Asts.TypeAst) -> SemanticError:
            self.add_info(
                pos=super_class.pos,
                tag=f"Super class '{super_class}' extended here")

            self.add_error(
                pos=base_method.pos,
                tag="Non-virtual method on base class.",
                msg=f"The super member '{base_method}' is not virtual and cannot be overridden in the subclass.",
                tip="Use a virtual method.")

            return self

    class SuperimpositionInheritanceDuplicateSuperclassError(SemanticError):
        """
        The SuperimpositionInheritanceDuplicateSuperclassError is raised if a type is superimposed twice over another
        type. The 2 matched types are symbolically equal, ie alias-aware, generically matched types.
        """

        def add(self, first_inheritance: Asts.TypeAst, second_inheritance: Asts.TypeAst) -> SemanticError:
            self.add_info(
                pos=first_inheritance.pos,
                tag=f"Type '{first_inheritance}' inherited here")

            self.add_error(
                pos=second_inheritance.pos,
                tag=f"Duplicate superimposition here",
                msg="Cannot superimpose the same type twice",
                tip="Remove the second superimposition definition")

            return self

    class SuperimpositionInheritanceCyclicInheritanceError(SemanticError):
        """
        The SuperimpositionInheritanceCyclicSuperclassError is raised two types inherit each other. Inheritance trees,
        whilst supporting multi-parents, must be loop free.
        """

        def add(self, first_inheritance: Asts.TypeAst, second_inheritance: Asts.TypeAst) -> SemanticError:
            self.add_info(
                pos=first_inheritance.pos,
                tag=f"Valid inheritance defined here")

            self.add_error(
                pos=second_inheritance.pos,
                tag=f"Cyclic superimposition here",
                msg="Two types cannot superimpose each other",
                tip="Remove the second superimposition definition")

            return self

    class SuperimpositionUnconstrainedGenericParameterError(SemanticError):
        """
        The SuperimpositionUnconstrainedGenericParameterError is raised if a generic parameter is unconstrained in a
        superimposition. All generic parameters must be constrained to the overridden type, as there is no way to pass a
        generic argument into a superimposition. Same as "non-inferrable" generic parameters.
        """

        def add(self, unconstrained_generic_parameter: Asts.GenericParameterAst, type: Asts.TypeAst) -> SemanticError:
            self.add_info(
                pos=type.pos,
                tag="Type defined here")

            self.add_error(
                pos=unconstrained_generic_parameter.pos,
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
                pos=optional_generic_parameter.pos,
                tag="Optional generic parameter.",
                msg=f"The generic parameter '{optional_generic_parameter}' is optional.",
                tip="Remove the optional generic parameter.")

            return self

    class LoopTooManyControlFlowStatementsError(SemanticError):
        """
        The LoopTooManyControlFlowStatementsError is raised if a loop has too many control flow statements. The maximum
        number of control flow statements is equal to the loop depth.
        """

        def add(self, loop: Asts.LoopExpressionAst, loop_control: Asts.LoopControlFlowStatementAst, number_of_controls: int, depth_of_loop: int) -> SemanticError:
            self.add_info(
                pos=loop.pos,
                tag="Loop defined here")

            self.add_error(
                pos=loop_control.pos,
                tag="Too many control flow statements.",
                msg=f"The loop has {number_of_controls} control flow statements, but the loop depth is only {depth_of_loop}.",
                tip="Remove some control flow statements from the loop.")

            return self

    class TupleElementBorrowedError(SemanticError):
        """
        The TupleElementBorrowedError is raised if an element in a tuple is borrowed. Array elements cannot be borrowed,
        and must all be owned.
        """

        def add(self, element: Asts.ExpressionAst, borrow_location: Ast) -> SemanticError:
            self.add_info(
                pos=borrow_location.pos,
                tag="Tuple element borrowed here")

            self.add_error(
                pos=element.pos,
                tag="Tuple element borrowed.",
                msg="Tuple elements cannot be borrowed.",
                tip="Remove the borrow from the tuple element.")

            return self

    class CaseBranchesConflictingTypesError(SemanticError):
        """
        The CaseBranchesConflictingTypesError is raised if the branches in a case statement return conflicting types,
        and the case expression is being used for assignment.
        """

        def add(self, return_type_1: InferredType, return_type_2: InferredType) -> SemanticError:
            self.add_info(
                pos=return_type_1.type.pos,
                tag=f"Branch inferred as '{return_type_1}'")

            self.add_error(
                pos=return_type_2.type.pos,
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
                pos=condition.pos,
                tag="Case expression defined here")

            self.add_error(
                pos=final_branch.pos,
                tag="Missing else branch.",
                msg="The case statement is missing an else branch.",
                tip="Add an else branch to the case statement.")

            return self

    class CaseBranchesElseBranchNotLastError(SemanticError):
        """
        The CaseBranchesElseBranchNotLastError is raised if the else branch is not the last branch in a case statement.
        """

        def add(self, else_branch: Asts.CaseExpressionBranchAst, last_branch: Asts.CaseExpressionBranchAst) -> SemanticError:
            self.add_info(
                pos=else_branch.pos,
                tag="Else branch defined here")

            self.add_error(
                pos=last_branch.pos,
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
                pos=first_pattern.pos,
                tag="First destructure pattern defined here")

            self.add_error(
                pos=second_pattern.pos,
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

        def add(self, first_multi_skip: Asts.PatternVariantDestructureSkipNArgumentsAst, second_multi_skip: Asts.PatternVariantDestructureSkipNArgumentsAst) -> SemanticError:
            self.add_info(
                pos=first_multi_skip.pos,
                tag="First multi-skip defined here")

            self.add_error(
                pos=second_multi_skip.pos,
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

        def add(self, object_destructure: Asts.LocalVariableDestructureObjectAst, bound_multi_skip: Asts.PatternVariantDestructureSkipNArgumentsAst) -> SemanticError:
            self.add_info(
                pos=object_destructure.pos,
                tag="Object destructure defined here")

            self.add_error(
                pos=bound_multi_skip.pos,
                tag="Multi-skip with binding found.",
                msg="Multi-skip cannot contain a binding.",
                tip="Remove the binding from the multi-skip.")

            return self

    class VariableTupleDestructureTupleSizeMismatchError(SemanticError):
        """
        The VariableTupleDestructureTupleSizeMismatchError is raised if a variable tuple-destructure has a different
        number of elements than the tuple being destructured. For example, "let (a, b) = (1, 2, 3)" is invalid.
        """

        def add(self, lhs: Asts.LocalVariableDestructureTupleAst, lhs_count: int, rhs: Ast, rhs_count: int) -> SemanticError:
            self.add_info(
                pos=lhs.pos,
                tag=f"{lhs_count}-tuple destructure defined here")

            self.add_error(
                pos=rhs.pos,
                tag=f"Type inferred as a {rhs_count}-tuple here",
                msg="The tuple destructure has a different number of elements than the tuple being destructure.",
                tip="Change the tuple destructure to have the same number of elements as the tuple.")

            return self

    class VariableArrayDestructureArraySizeMismatchError(SemanticError):
        """
        The VariableArrayDestructureArraySizeMismatchError is raised if a variable array-destructure has a different
        number of elements than the array being destructured. For example, "let [a, b] = [1, 2, 3]" is invalid.
        """

        def add(self, lhs: Asts.LocalVariableDestructureArrayAst, lhs_count: int, rhs: Ast, rhs_count: int) -> SemanticError:
            self.add_info(
                pos=lhs.pos,
                tag=f"{lhs_count}-array destructure defined here")

            self.add_error(
                pos=rhs.pos,
                tag=f"Type inferred as a {rhs_count}-array here",
                msg="The array destructure has a different number of elements than the array being destructure.",
                tip="Change the array destructure to have the same number of elements as the array.")

            return self

    class AsyncFunctionCallInvalidTargetError(SemanticError):
        """
        The AsyncFunctionCallInvalidTargetError is raised if the target of an async function call is not a function. For
        example, whilst "async f()" is valid, "async 5" is not.
        """

        def add(self, async_modifier: Ast, target: Ast) -> SemanticError:
            self.add_info(
                pos=async_modifier.pos,
                tag="Async modifier used here")

            self.add_error(
                pos=target.pos,
                tag="Invalid async function call target.",
                msg="The target of an async function call must be a function.",
                tip="Remove the async call modifier, or change the target to a function.")

            return self

    class ObjectInitializerMultipleDefArgumentsError(SemanticError):
        """
        The ObjectInitializerMultipleDefArgumentsError is raised if an object initializer has multiple default
        arguments. Only one default argument is allowed. For example, "Type(else=a, else=b)" is invalid".
        """

        def add(self, first_else: Ast, second_else: Ast) -> SemanticError:
            self.add_info(
                pos=first_else.pos,
                tag="First default argument defined here")

            self.add_error(
                pos=second_else.pos,
                tag="Second default argument defined here",
                msg="Only one default argument is allowed in an object initializer.",
                tip="Remove the second default argument.")

            return self

    class ObjectInitializerAbstractClassError(SemanticError):
        """
        The ObjectInitializerAbstractClassError is raised if an object initializer is used on an abstract class. An
        abstract class cannot be instantiated. An abstract class is defined as a class with 1 or more non-implemented
        abstract methods.
        """

        def add(self, class_type: Asts.TypeAst) -> SemanticError:
            self.add_error(
                pos=class_type.pos,
                tag=f"Abstract type '{class_type}' initialized here",
                msg="An abstract class cannot be instantiated.",
                tip="Use a non-abstract class instead.")

            return self
