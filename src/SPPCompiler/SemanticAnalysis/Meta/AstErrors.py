from __future__ import annotations
from typing import TYPE_CHECKING

from SPPCompiler.Utils.Errors import SemanticError

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import *


class AstErrors:
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
