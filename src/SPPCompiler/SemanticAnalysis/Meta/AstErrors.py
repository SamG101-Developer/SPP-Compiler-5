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
            tag=f"Non-{white_list.title()} defined here.",
            msg=f"The annotation '{annotation}' can only be applied to {white_list}.",
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
