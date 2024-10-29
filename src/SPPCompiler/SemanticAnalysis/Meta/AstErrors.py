from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from SPPCompiler.Utils.Errors import SemanticError

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import *


class AstErrors:
    # ANNOTATION ERRORS

    @staticmethod
    def INVALID_ANNOTATION_APPLICATION(annotation: IdentifierAst, applied_to: Ast, white_list: str) -> SemanticError:
        e = SemanticError()
        e.add_info(annotation.pos, f"Annotation '{annotation}' defined here")
        e.add_error(
            pos=applied_to.pos,
            tag=f"Non-{white_list} AST defined here.",
            msg=f"The '{annotation}' annotation can only be applied to {white_list} ASTs.",
            tip=f"Remove the annotation from here.")
        return e

    @staticmethod
    def UNKNOWN_ANNOTATION(annotation: IdentifierAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=annotation.pos,
            tag="Unknown annotation.",
            msg=f"The annotation '{annotation}' is not a valid annotation.",
            tip=f"Remove the annotation from here.")
        return e

    @staticmethod
    def DUPLICATE_ANNOTATION(first_annotation: IdentifierAst, second_annotation: IdentifierAst) -> SemanticError:
        e = SemanticError()
        e.add_info(first_annotation.pos, f"Annotation '{first_annotation}' applied here")
        e.add_error(
            pos=second_annotation.pos,
            tag="Duplicate annotation.",
            msg=f"The annotation '{second_annotation}' is already applied.",
            tip=f"Remove the duplicate annotation.")
        return e

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

    # PARAMETER ERRORS

    @staticmethod
    def INVALID_PARAMETER_ORDER(first_parameter: FunctionParameterAst, second_parameter: FunctionParameterAst) -> SemanticError:
        e = SemanticError()
        e.add_info(first_parameter.pos, f"Parameter '{first_parameter}' defined here")
        e.add_error(
            pos=second_parameter.pos,
            tag="Invalid parameter order.",
            msg=f"The parameter '{second_parameter}' is in the wrong position.",
            tip=f"Move the parameter to the correct position.")
        return e

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
    def UNDEFINED_IDENTIFIER(identifier: IdentifierAst, closest_match: Optional[str]) -> SemanticError:
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
