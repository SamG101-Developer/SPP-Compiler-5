from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class AnnotationAst(Ast, Stage1_PreProcessor, Stage4_SemanticAnalyser):
    tok_at: TokenAst
    name: IdentifierAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_at.print(printer),
            self.name.print(printer) + " "]
        return "".join(string)

    def pre_process(self, context: PreProcessingContext) -> None:
        # Import the necessary classes for type-comparisons to ensure annotation compatibility.
        from SPPCompiler.SemanticAnalysis import FunctionPrototypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstVisibility import VisibilityEnabled, AstVisibility
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Pre-process the name of this annotation.
        match self.name.value:

            case "virtual_method":
                # The "virtual_method" annotation can only be applied to functions.
                if not isinstance(context, FunctionPrototypeAst):
                    raise AstErrors.INVALID_ANNOTATION_APPLICATION(self.name, context, "function")
                context._virtual = True

            case "abstract_method":
                # The "abstract_method" annotation can only be applied to functions.
                if not isinstance(context, FunctionPrototypeAst):
                    raise AstErrors.INVALID_ANNOTATION_APPLICATION(self.name, context, "function")
                context._abstract = True

            case "public":
                # The "public", access modifier annotation can only be applied to visibility enabled objects.
                if not isinstance(context, VisibilityEnabled):
                    raise AstErrors.INVALID_ANNOTATION_APPLICATION(self.name, context, "visibility-enabled")
                context.visibility = AstVisibility.Public

            case "protected":
                # The "protected", access modifier annotation can only be applied to visibility enabled objects.
                if not isinstance(context, VisibilityEnabled):
                    raise AstErrors.INVALID_ANNOTATION_APPLICATION(self.name, context, "visibility-enabled")
                context.visibility = AstVisibility.Protected

            case "private":
                # The "private", access modifier annotation can only be applied to visibility enabled objects.
                if not isinstance(context, VisibilityEnabled):
                    raise AstErrors.INVALID_ANNOTATION_APPLICATION(self.name, context, "visibility-enabled")
                context.visibility = AstVisibility.Private

            # The "static" annotation can only be applied to functions.
            case _:
                raise AstErrors.UNKNOWN_ANNOTATION(self.name)

    def analyse_semantics(self, scope_handler: ScopeManager, **kwargs) -> None:
        # Todo: Prevent duplicate annotations.
        ...


__all__ = ["AnnotationAst"]
