from __future__ import annotations
from abc import ABC, abstractmethod
from colorama import Fore, Style
from dataclasses import dataclass
from fastenum import Enum
from typing import List, NoReturn, Optional, Tuple, TYPE_CHECKING

from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter


if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import *


class SemanticError(ABC, BaseException):
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

    @abstractmethod
    def add(*args, **kwargs) -> None:
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

        def add(self, annotation: IdentifierAst, applied_to: Ast, allow_list: str) -> None:
            self.add_info(
                pos=annotation.pos,
                tag=f"Annotation '{annotation}' defined here")

            self.add_error(
                pos=applied_to.pos,
                tag=f"Non-{allow_list} AST defined here.",
                msg=f"The '{annotation}' annotation can only be applied to {allow_list} ASTs.",
                tip=f"Remove the annotation from here.")

    class AnnotationInvalidError(SemanticError):
        """
        The AnnotationInvalidError is raised if a non-standard annotation is used in the code. This includes using the
        "@foo" annotation, which is not a valid annotation in the language. Only standard annotations are allowed, such
        as "@public", "@no_impl" etc.
        """

        def add(self, annotation: IdentifierAst) -> None:
            self.add_error(
                pos=annotation.pos,
                tag="Invalid annotation.",
                msg=f"The annotation '{annotation}' is not a valid annotation.",
                tip=f"Remove the annotation from here.")

    class AnnotationDuplicateError(SemanticError):
        """
        The AnnotationDuplicateError is raised if the same annotation is applied multiple times to the same AST. Because
        the standard annotations modify ASTs before symbol generation, applying the same annotation twice is redundant
        and therefore not allowed.
        """

        def add(self, first_annotation: IdentifierAst, second_annotation: IdentifierAst) -> None:
            self.add_info(
                pos=first_annotation.pos,
                tag=f"Annotation '{first_annotation}' applied here")

            self.add_error(
                pos=second_annotation.pos,
                tag="Duplicate annotation.",
                msg=f"The annotation '{second_annotation}' is already applied.",
                tip=f"Remove the duplicate annotation.")

    class AnnotationConflictError(SemanticError):
        """
        The AnnotationConflictError is raised if there are 2 annotations on the same object that either have conflicting
        behaviour / are mutually exclusive. For example, using "@hot" and "@cold" on the same function would raise this
        error.
        """

        def add(self, first_annotation: IdentifierAst, conflicting_annotation: IdentifierAst) -> None:
            self.add_info(
                pos=first_annotation.pos,
                tag=f"Annotation '{first_annotation}' applied here")

            self.add_error(
                pos=conflicting_annotation.pos,
                tag="Conflicting annotation.",
                msg=f"The annotation '{conflicting_annotation}' conflicts with the first annotation.",
                tip=f"Remove the conflicting annotation.")

    class AnnotationRedundantError(SemanticError):
        """
        The AnnotationRedundantError is raised if there are 2 annotations on the same object and one makes the other
        redundant. For example, using "@abstractmethod" makes @virtualmethod" redundant as an abstract method is
        automatically virtual.
        """

        def add(self, first_annotation: IdentifierAst, redundant_annotation: IdentifierAst) -> None:
            self.add_info(
                pos=first_annotation.pos,
                tag=f"Annotation '{first_annotation}' applied here")

            self.add_error(
                pos=redundant_annotation.pos,
                tag="Redundant annotation.",
                msg=f"The annotation '{redundant_annotation}' is made redundant by the '{first_annotation}' annotation.",
                tip=f"Remove the redundant annotation.")


class AstErrors:
    # IDENTIFIER ERRORS

    @staticmethod
    def DUPLICATE_IDENTIFIER(first_identifier: IdentifierAst, second_identifier: IdentifierAst, what: str) -> SemanticError:
        e = SemanticError()
        e.add_info(first_identifier.pos, f"{what.capitalize()} '{first_identifier}' defined here")
        e.add_error(
            pos=second_identifier.pos,
            tag=f"Duplicate {what}.",
            msg=f"The {what} '{second_identifier}' is already defined.",
            tip=f"Remove or rename the duplicate {what}.")
        return e

    # ORDER ERRORS

    @staticmethod
    def INVALID_ORDER(first: Ast, second: Ast, what: str) -> SemanticError:
        e = SemanticError()
        e.add_info(first.pos, f"{what.capitalize()} '{first}' defined here")
        e.add_error(
            pos=second.pos,
            tag=f"Invalid {what} order.",
            msg=f"The {what} '{second}' is in the wrong position.",
            tip=f"Move the {what} to the correct position.")
        return e

    # PARAMETER ERRORS

    @staticmethod
    def MULTIPLE_SELF_PARAMETERS(first_parameter: FunctionParameterAst, second_parameter: FunctionParameterAst) -> SemanticError:
        e = SemanticError()
        e.add_info(first_parameter.pos, f"Parameter '{first_parameter}' defined here")
        e.add_error(
            pos=second_parameter.pos,
            tag="Multiple 'self' parameters.",
            msg=f"Only one 'self' parameter is allowed.",
            tip=f"Remove the duplicate 'self' parameter.")
        return e

    @staticmethod
    def MULTIPLE_VARIADIC_PARAMETERS(first_parameter: FunctionParameterAst, second_parameter: FunctionParameterAst) -> SemanticError:
        e = SemanticError()
        e.add_info(first_parameter.pos, f"Parameter '{first_parameter}' defined here")
        e.add_error(
            pos=second_parameter.pos,
            tag="Multiple variadic parameters.",
            msg=f"Only one variadic parameter is allowed.",
            tip=f"Remove the duplicate variadic parameter.")
        return e

    @staticmethod
    def OPTIONAL_PARAM_REQUIRES_NON_BORROW(convention: ConventionAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=convention.pos,
            tag="Optional parameter requires non-borrow convention.",
            msg="Optional parameters cannot have borrow conventions.",
            tip="Change the convention to a move convention.")
        return e

    # FUNCTION ERRORS

    @staticmethod
    def INVALID_COROUTINE_RETURN_TYPE(return_type: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=return_type.pos,
            tag="Invalid coroutine return type.",
            msg="The return type of a coroutine must be a generator.",
            tip="Change the return type to one of 'GenMov', 'GenMut' or 'GenRef'.")
        return e

    @staticmethod
    def GEN_OUTSIDE_COROUTINE(tok_gen: TokenAst, tok_fun: TokenAst) -> SemanticError:
        e = SemanticError()
        e.add_info(tok_fun.pos, f"Subroutine defined here")
        e.add_error(
            pos=tok_gen.pos,
            tag="Yielding outside coroutine.",
            msg="The 'gen' keyword can only be used inside a coroutine.",
            tip="Use a coroutine instead of a subroutine.")
        return e

    @staticmethod
    def RET_OUTSIDE_SUBROUTINE(tok_ret: TokenAst, tok_cor: TokenAst) -> SemanticError:
        e = SemanticError()
        e.add_info(tok_cor.pos, f"Coroutine defined here")
        e.add_error(
            pos=tok_ret.pos,
            tag="Returning outside subroutine.",
            msg="The 'ret' keyword can only be used inside a subroutine.",
            tip="Use a subroutine instead of a coroutine.")
        return e

    @staticmethod
    def MISSING_RETURN_STATEMENT(final_member: Ast, function_return_type: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_info(function_return_type.pos, f"Function return type '{function_return_type}' defined here")
        e.add_error(
            pos=final_member.pos,
            tag="Missing return statement.",
            msg="The function does not have a return statement.",
            tip="Add a return statement to the function.")
        return e

    @staticmethod
    def INVALID_ARGUMENT_NAMES(parameter_names: Seq[Ast], invalid_argument: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(parameter_names[0].pos, f"Parameter names defined here")
        e.add_error(
            pos=invalid_argument.pos,
            tag="Invalid argument name.",
            msg="The argument name is not valid.",
            tip="Use a valid argument name.")
        return e

    @staticmethod
    def MISSING_ARGUMENT_NAMES(missing_arguments: Seq[Ast], what: str, what_singular: str) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=missing_arguments[0].pos,
            tag=f"Missing {what_singular} names.",
            msg=f"The {what} is missing the {what_singular} '{missing_arguments.join(", ")}'.",
            tip=f"Add the missing {what_singular} names.")
        return e

    @staticmethod
    def NO_VALID_FUNCTION_SIGNATURES(function_call: Ast, signatures: str, attempted: str) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=function_call.pos,
            tag="Invalid arguments for function call",
            msg="There are no overloads accepting the given arguments",
            tip=f"\n\t{signatures.replace("\n", "\n\t")}\n\nAttempted signature:\n\t{attempted}")
        return e

    @staticmethod
    def AMBIGUOUS_FUNCTION_SIGNATURES(function_call: Ast, signatures: str) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=function_call.pos,
            tag="Ambiguous function call",
            msg="There are multiple overloads accepting the given arguments",
            tip=f"\n\t{signatures.replace("\n", "\n\t")}")
        return e

    @staticmethod
    def CANNOT_CALL_ABSTRACT_METHOD(function: IdentifierAst, function_call: PostfixExpressionOperatorFunctionCallAst) -> SemanticError:
        e = SemanticError()
        e.add_info(function.pos, "Function annotated as abstract")
        e.add_error(
            pos=function_call.pos,
            tag="Abstract method called here.",
            msg="Cannot call abstract methods.",
            tip="Call the method on a subtype")
        return e

    # GENERAL SCOPE ERRORS

    @staticmethod
    def UNREACHABLE_CODE(return_ast: RetStatementAst, next_ast: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(return_ast.pos, f"Return statement defined here")
        e.add_error(
            pos=next_ast.pos,
            tag="Unreachable code.",
            msg="The code after the return statement is unreachable.",
            tip="Remove the unreachable code or move the return statement.")
        return e

    # NUMER ERRORS

    @staticmethod
    def NUMBER_OUT_OF_RANGE(number: IntegerLiteralAst | FloatLiteralAst, min: int, max: int, what: str) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=number.pos,
            tag=f"{what.capitalize()} out of range.",
            msg=f"The {what} '{number}' is out of range [{min}, {max}].",
            tip=f"Change the number to be within the range, or change the type specifier.")
        return e

    # IDENTIFIER ERRORS

    @staticmethod
    def UNDEFINED_IDENTIFIER(identifier: IdentifierAst | GenericIdentifierAst, closest_match: Optional[str]) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=identifier.pos,
            tag="Undefined identifier.",
            msg=f"The identifier '{identifier}' is not defined.",
            tip=f"Did you mean '{closest_match}'?" if closest_match else "Define the identifier.")
        return e

    # TYPE ERRORS

    @staticmethod
    def INVALID_VOID_USE(type: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=type.pos,
            tag="Invalid use of void.",
            msg="The void type cannot be used in this context.",
            tip="Change the type to a valid type.")
        return e

    @staticmethod
    def TYPE_MISMATCH(existing_ast: Ast, existing_type: InferredType, incoming_ast: Ast, incoming_type: InferredType) -> SemanticError:
        e = SemanticError()
        e.add_info(existing_ast.pos, f"Type inferred as '{existing_type}' here")  # todo: add potential alias's old type
        e.add_error(
            pos=incoming_ast.pos,
            tag=f"Type inferred as '{incoming_type}' here",
            msg="Type mismatch.",
            tip="Change the type to match the expected type.")
        return e

    @staticmethod
    def UNINFERRED_GENERIC_PARAMETER(generic_parameter: GenericParameterAst, type: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_info(type.pos, "Type created here")
        e.add_error(
            pos=generic_parameter.pos,
            tag="Uninferred generic parameter.",
            msg="The generic parameter is not inferred.",
            tip="Infer the generic parameter.")
        return e

    @staticmethod
    def INVALID_PLACE_FOR_GENERIC(lhs: Ast, lhs_type: TypeAst, access_token: TokenAst) -> SemanticError:
        e = SemanticError()
        e.add_info(lhs.pos, f"Generic type '{lhs_type}' inferred here.")
        e.add_error(
            pos=access_token.pos,
            tag="Member access on generic type.",
            msg="Generic types do not support member access.",
            tip="Use a concrete type instead of a generic type.")
        return e

    # ARRAY ERRORS

    @staticmethod
    def ARRAY_ELEMENTS_DIFFERENT_TYPES(element_type_1: TypeAst, element_type_2: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_info(element_type_1.pos, f"Element type '{element_type_1}' defined here")
        e.add_error(
            pos=element_type_2.pos,
            tag="Array elements have different types.",
            msg="All elements in an array must have the same type.",
            tip="Change the element types to be the same.")
        return e

    @staticmethod
    def ARRAY_BORROWED_ELEMENT(element: ExpressionAst, borrow_location: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(borrow_location.pos, f"Array element borrowed here")
        e.add_error(
            pos=element.pos,
            tag="Array element borrowed.",
            msg="Array elements cannot be borrowed.",
            tip="Remove the borrow from the array element.")
        return e

    # MEMORY ERRORS

    @staticmethod
    def INCONSISTENTLY_INITIALIZED_MEMORY(ast: ExpressionAst, branch_1: Tuple[PatternBlockAst, bool], branch_2: Tuple[PatternBlockAst, bool]) -> SemanticError:
        e = SemanticError()
        e.add_info(branch_1[0].pos, f"Symbol {ast} {"initialized" if branch_1[1] else "moved"} in this branch")
        e.add_info(branch_2[0].pos, f"Symbol {ast} {"initialized" if branch_2[1] else "moved"} in this branch")
        e.add_error(
            pos=ast.pos,
            tag="Inconsistently initialized symbol.",
            msg="Branches inconsistently initialize the symbol.",
            tip="Ensure the symbol is consistently initialized.")
        return e

    @staticmethod
    def INCONSISTENT_PINNED_MEMORY(ast: ExpressionAst, branch_1: Tuple[PatternBlockAst, bool], branch_2: Tuple[PatternBlockAst, bool]) -> SemanticError:
        e = SemanticError()
        e.add_info(branch_1[0].pos, f"Symbol {ast} {"not" if branch_1[1] else "is"} pinned in this branch")
        e.add_info(branch_2[0].pos, f"Symbol {ast} {"not" if branch_2[1] else "is"} pinned in this branch")
        e.add_error(
            pos=ast.pos,
            tag="Inconsistently pinned symbol.",
            msg="Branches inconsistently pin the symbol.",
            tip="Ensure the symbol is consistently pinned.")
        return e

    @staticmethod
    def USING_UNINITIALIZED_MEMORY(ast: ExpressionAst, move_location: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(move_location.pos, f"Symbol {ast} moved here")
        e.add_error(
            pos=ast.pos,
            tag="Using uninitialized memory.",
            msg="The memory has already been moved.",
            tip="Ensure the memory is initialized before use.")
        return e

    @staticmethod
    def USING_PARTIALLY_INITIALIZED_MEMORY(ast: ExpressionAst, partial_move_location: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(partial_move_location.pos, f"Symbol {ast} partially moved here")
        e.add_error(
            pos=ast.pos,
            tag="Using partially initialized memory.",
            msg="The memory has already been partially moved.",
            tip="Ensure the memory is fully initialized before use.")
        return e

    @staticmethod
    def MOVING_FROM_BORROWED_CONTEXT(move_location: Ast, borrow_location: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(borrow_location.pos, f"Symbol borrowed here")
        e.add_error(
            pos=move_location.pos,
            tag="Moving from borrowed context.",
            msg="The memory is borrowed and cannot be moved.",
            tip="Remove the move operation.")
        return e

    @staticmethod
    def MOVING_PINNED_MEMORY(move_location: Ast, pin_location: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(pin_location.pos, f"Symbol pinned here")
        e.add_error(
            pos=move_location.pos,
            tag="Moving pinned memory.",
            msg="The memory is pinned and cannot be moved.",
            tip="Remove the move operation.")
        return e

    @staticmethod
    def MEMORY_OVERLAP_CONFLICT(overlap: Ast, ast: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(overlap.pos, f"Memory overlap defined here")
        e.add_error(
            pos=ast.pos,
            tag="Memory overlap conflict.",
            msg="The memory overlap conflicts with another memory use.",
            tip="Remove the memory overlap conflict.")
        return e

    @staticmethod
    def UNPINNED_BORROW(ast: Ast, async_or_coro_definition: Ast, is_async: bool) -> SemanticError:
        e = SemanticError()
        e.add_info(async_or_coro_definition.pos, f"{"Async" if is_async else "Coroutine"} definition here")
        e.add_error(
            pos=ast.pos,
            tag="Unpinned borrow.",
            msg=f"A{"n asynchronous call" if is_async else " coroutine"} cannot take an unpinned borrow.",
            tip="Pin the borrow.")
        return e

    # ASSIGNMENT ERRORS

    @staticmethod
    def CANNOT_MUTATE_IMMUTABLE_SYMBOL(ast: ExpressionAst, move_location: Ast, immutable_definition: Ast) -> SemanticError:
        e = SemanticError()
        e.add_info(immutable_definition.pos, f"Symbol '{ast}' defined as immutable here")
        e.add_error(
            pos=move_location.pos,
            tag="Attempting to mutate immutable symbol.",
            msg="The symbol is immutable and cannot be mutated.",
            tip="Change the symbol to be mutable.")
        return e

    @staticmethod
    def INVALID_ASSIGNMENT_LHS_EXPR(lhs: ExpressionAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=lhs.pos,
            tag="Invalid assignment LHS expression.",
            msg="The expression is not valid for assignment.",
            tip="Use a valid expression for assignment.")
        return e

    @staticmethod
    def INVALID_COMPOUND_ASSIGNMENT_LHS_EXPR(lhs: ExpressionAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=lhs.pos,
            tag="Invalid compound assignment LHS expression.",
            msg="The expression is not valid for compound assignment.",
            tip="Use a valid expression for compound assignment.")
        return e

    # EXPRESSION ERRORS

    @staticmethod
    def INVALID_EXPRESSION(expression: ExpressionAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=expression.pos,
            tag="Invalid expression.",
            msg="The expression is not valid.",
            tip="Use a non-type and non-token expression.")
        return e

    @staticmethod
    def CONDITION_NOT_BOOLEAN(condition: ExpressionAst, type: TypeAst, what: str) -> SemanticError:
        e = SemanticError()
        e.add_info(condition.pos, f"{what.capitalize()} condition defined as '{type}' here")
        e.add_error(
            pos=condition.pos,
            tag="Condition not boolean.",
            msg=f"The condition for a {what} must be a boolean type.",
            tip="Change the condition to be a boolean type.")
        return e

    # MEMBER ACCESS ERRORS

    @staticmethod
    def STATIC_MEMBER_ACCESS_EXPECTED(lhs: Ast, access_token: TokenAst) -> SemanticError:
        e = SemanticError()
        e.add_info(lhs.pos, f"Static expression defined here")
        e.add_error(
            pos=access_token.pos,
            tag="Runtime member access found.",
            msg="The member access operator '.' can only be used on runtime expressions.",
            tip="Use the member access operator '::' instead of '.'.")
        return e

    @staticmethod
    def RUNTIME_MEMBER_ACCESS_EXPECTED(lhs: Ast, access_token: TokenAst) -> SemanticError:
        e = SemanticError()
        e.add_info(lhs.pos, f"Runtime expression defined here")
        e.add_error(
            pos=access_token.pos,
            tag="Static member access found.",
            msg="The member access operator '::' can only be used on static expressions.",
            tip="Use the member access operator '.' instead of '::'.")
        return e

    @staticmethod
    def AMBIGUOUS_MEMBER_ACCESS(member: IdentifierAst, scopes: Seq[IdentifierAst]) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=member.pos,
            tag=f"Ambiguous member access: {scopes.join(", ")}",
            msg="The member access is ambiguous.",
            tip="Use 'std::upcast[T](...)' to select the base class.")
        return e

    @staticmethod
    def MEMBER_ACCESS_NON_INDEXABLE(lhs: Ast, lhs_type: TypeAst, access_token: TokenAst) -> SemanticError:
        e = SemanticError()
        e.add_info(lhs.pos, f"Type '{lhs_type}' inferred here.")
        e.add_error(
            pos=access_token.pos,
            tag="Member access on non-indexable type.",
            msg="The type does not support member access.",
            tip="Use a type that supports member access.")
        return e

    @staticmethod
    def MEMBER_ACCESS_OUT_OF_BOUNDS(lhs: Ast, lhs_type: TypeAst, number_token: TokenAst) -> SemanticError:
        e = SemanticError()
        e.add_info(lhs.pos, f"{lhs_type.types[-1].generic_argument_group.arguments.length}-tuple inferred here.")
        e.add_error(
            pos=number_token.pos,
            tag="Member access out of bounds.",
            msg="The member access is out of bounds.",
            tip="Use a valid member access.")
        return e

    # SUPERIMPOSITION ERRORS

    @staticmethod
    def SUP_MEMBER_INVALID(new_method: IdentifierAst, super_class: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_info(super_class.pos, f"Super class '{super_class}' extended here")
        e.add_error(
            pos=new_method.pos,
            tag="Invalid member.",
            msg=f"The subclass member '{new_method}' does not exist in the superclass '{super_class}'.",
            tip="Use a valid super member.")
        return e

    @staticmethod
    def SUP_ABSTRACT_MEMBER_NOT_OVERRIDEN(base_method: IdentifierAst, super_class: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_info(super_class.pos, f"Super class '{super_class}' extended here")
        e.add_error(
            pos=base_method.pos,
            tag="Abstract method on base class",
            msg=f"The super member '{base_method}' has not been overridden in the subclass",
            tip="Override the super member in the subclass")
        return e

    @staticmethod
    def SUP_UNCONSTRAINED_GENERIC_PARAMETER(unconstrained_parameter: GenericParameterAst, type: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_info(type.pos, "Type defined here")
        e.add_error(
            pos=unconstrained_parameter.pos,
            tag="Unconstrained generic parameter",
            msg=f"The generic parameter '{unconstrained_parameter.name}' is unconstrained.",
            tip="Remove this generic parameter")
        return e

    # PATTERN ERRORS

    @staticmethod
    def INVALID_PATTERN_DESTRUCTOR_OBJECT(condition: ExpressionAst, condition_type: TypeAst, destructured_type: TypeAst) -> SemanticError:
        e = SemanticError()
        e.add_info(condition.pos, f"Condition inferred as '{condition_type}' here")
        e.add_error(
            pos=destructured_type.pos,
            tag=f"Invalid pattern destructure type '{destructured_type}'.",
            msg="The pattern destructor object is not valid.",
            tip="Use a valid pattern destructor object.")
        return e

    # LOOP ERRORS

    @staticmethod
    def CONTROL_FLOW_TOO_MANY_CONTROLS(loop: LoopExpressionAst, loop_control: LoopControlFlowStatementAst, number_of_controls: int, depth_of_loop: int) -> SemanticError:
        e = SemanticError()
        e.add_info(loop.pos, f"Loop defined here")
        e.add_error(
            pos=loop_control.pos,
            tag="Too many control flow statements.",
            msg=f"The loop has {number_of_controls} control flow statements, but the loop depth is only {depth_of_loop}.",
            tip="Remove some control flow statements from the loop.")
        return e

    @staticmethod
    def INVALID_ITERABLE_TYPE(iterable: ExpressionAst, type: InferredType) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=iterable.pos,
            tag=f"Iterable inferred as '{type}'",
            msg="The iterable type is not valid.",
            tip="Use a generator type.")
        return e
