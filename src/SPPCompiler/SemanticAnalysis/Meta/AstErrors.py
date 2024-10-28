from __future__ import annotations
from typing import TYPE_CHECKING

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
            tip=f"Remove the annotation from here")
        return e

    @staticmethod
    def UNKNOWN_ANNOTATION(annotation: IdentifierAst) -> SemanticError:
        e = SemanticError()
        e.add_error(
            pos=annotation.pos,
            tag="Unknown annotation.",
            msg=f"The annotation '{annotation}' is not a valid annotation.",
            tip=f"Remove the annotation from here")
        return e

    @staticmethod
    def DUPLICATE_ANNOTATION(first_annotation: IdentifierAst, second_annotation: IdentifierAst) -> SemanticError:
        e = SemanticError()
        e.add_info(first_annotation.pos, f"Annotation '{first_annotation}' applied here")
        e.add_error(
            pos=second_annotation.pos,
            tag="Duplicate annotation.",
            msg=f"The annotation '{second_annotation}' is already applied.",
            tip=f"Remove the duplicate annotation")
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
            tip=f"Remove or rename the duplicate {what}")
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
            tip=f"Move the parameter to the correct position")
        return e

    @staticmethod
    def MULTIPLE_SELF_PARAMETERS(first_parameter: FunctionParameterAst, second_parameter: FunctionParameterAst) -> SemanticError:
        e = SemanticError()
        e.add_info(first_parameter.pos, f"Parameter '{first_parameter}' defined here")
        e.add_error(
            pos=second_parameter.pos,
            tag="Multiple 'self' parameters.",
            msg=f"Only one 'self' parameter is allowed.",
            tip=f"Remove the duplicate 'self' parameter")
        return e

    @staticmethod
    def MULTIPLE_VARIADIC_PARAMETERS(first_parameter: FunctionParameterAst, second_parameter: FunctionParameterAst) -> SemanticError:
        e = SemanticError()
        e.add_info(first_parameter.pos, f"Parameter '{first_parameter}' defined here")
        e.add_error(
            pos=second_parameter.pos,
            tag="Multiple variadic parameters.",
            msg=f"Only one variadic parameter is allowed.",
            tip=f"Remove the duplicate variadic parameter")
        return e
