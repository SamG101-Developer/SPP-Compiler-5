from __future__ import annotations

import copy
from dataclasses import dataclass
from fastenum import Enum
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


"""
Ideas:
- Allow all bocks (loop/case+branches/with) etc to have annotations
- @inline, @noinline, @hot, @cold for functions
- @likely, @unlikely, @fallthrough for case branches
- @unroll, @allow_infinite for loops => map to a special return type?
"""


class _Annotations(Enum):
    VirtualMethod = "virtual_method"
    AbstractMethod = "abstract_method"
    NonImplementedMethod = "no_impl"
    Public = "public"
    Protected = "protected"
    Private = "private"
    Cold = "cold"
    Hot = "hot"


@dataclass
class AnnotationAst(Ast, CompilerStages):
    tok_at: TokenAst
    name: IdentifierAst

    def __deepcopy__(self, memodict={}):
        # Create a deep copy of the AST.
        return AnnotationAst(self.pos, copy.deepcopy(self.tok_at), copy.deepcopy(self.name), _ctx=self._ctx)

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
        from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled, AstVisibility
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        super().pre_process(context)

        # Pre-process the name of this annotation.
        if self.name.value == _Annotations.VirtualMethod.value:
            # The "virtual_method" annotation can only be applied to functions.
            if not isinstance(context, FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "function")
            context._virtual = True

        elif self.name.value == _Annotations.AbstractMethod.value:
            # The "abstract_method" annotation can only be applied to functions.
            if not isinstance(context, FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "function")
            context._abstract = context._virtual = True

        elif self.name.value == _Annotations.NonImplementedMethod.value:
            # The "non_implemented_method" annotation can only be applied to functions.
            if not isinstance(context, FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "function")
            context._non_implemented = True

        elif self.name.value == _Annotations.Public.value:
            # The "public", access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(context, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "visibility-enabled")
            context.visibility = AstVisibility.Public

        elif self.name.value == _Annotations.Protected.value:
            # The "protected", access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(context, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "visibility-enabled")
            context.visibility = AstVisibility.Protected

        elif self.name.value == _Annotations.Private.value:
            # The "private", access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(context, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "visibility-enabled")
            context.visibility = AstVisibility.Private

        elif self.name.value == _Annotations.Cold.value:
            # The "cold" annotation can only be applied to functions.
            if not isinstance(context, FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "function")
            context._cold = True

        elif self.name.value == _Annotations.Hot.value:
            # The "hot" annotation can only be applied to functions.
            if not isinstance(context, FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context, "function")
            context._hot = True

        else:
            raise SemanticErrors.AnnotationInvalidError(self.name)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Prevent duplicate annotations from being applied to an AST.
        annotation_names = self._ctx.annotations.map_attr("name")
        if duplicate_annotations := annotation_names.filter(lambda a: a == self.name).remove(self.name):
            raise SemanticErrors.AnnotationDuplicateError(self.name, duplicate_annotations[0])


__all__ = ["AnnotationAst"]
