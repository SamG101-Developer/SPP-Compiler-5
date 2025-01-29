from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Self

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled, AstVisibility
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

"""
Todo - ideas:
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
    Hidden = "hidden"
    Cold = "cold"
    Hot = "hot"


@dataclass
class AnnotationAst(Ast, CompilerStages):
    tok_at: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkAt))
    name: Asts.IdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name

    def __deepcopy__(self, memodict: Dict = None) -> AnnotationAst:
        # Create a deep copy of the AST.
        return AnnotationAst(self.pos, self.tok_at, self.name, _ctx=self._ctx)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_at.print(printer),
            self.name.print(printer) + " "]
        return "".join(string)

    @std.override_method
    def pre_process(self, context: PreProcessingContext) -> None:
        # Import the necessary classes for type-comparisons to ensure annotation compatibility.
        super().pre_process(context)

        if self.name.value == _Annotations.VirtualMethod.value:
            # The "virtual_method" annotation can only be applied to function asts.
            if not isinstance(context, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(
                    self.name, context.name, "function")

            # The function ast must be a class method, not a free function.
            if isinstance(context._ctx, Asts.ModulePrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(
                    self.name, context.name, "class-method")

            # The "virtual_method" annotation cannot be applied to an "abstract_method" annotation.
            if context._abstract:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, context._abstract.name)

            context._virtual = self

        elif self.name.value == _Annotations.AbstractMethod.value:
            # The "abstract_method" annotation can only be applied to function asts.
            if not isinstance(context, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "function")

            # The function ast must be a class method, not a free function.
            if isinstance(context._ctx, Asts.ModulePrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "class-method")

            # The "abstract_method" annotation cannot be applied to a "virtual_method" annotation.
            if context._virtual:
                raise SemanticErrors.AnnotationConflictError().add(self.name, context._virtual.name)

            context._abstract = self

        elif self.name.value == _Annotations.NonImplementedMethod.value:
            # The "non_implemented_method" annotation can only be applied to functions.
            if not isinstance(context, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "function")
            context._non_implemented = self

        elif self.name.value == _Annotations.Public.value:
            # The "public" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(context, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "visibility-enabled")
            if context._visibility[1] and context._visibility[0] != AstVisibility.Public:
                raise SemanticErrors.AnnotationConflictError().add(self.name, context._visibility[1].name)
            context._visibility = (AstVisibility.Public, self)

        elif self.name.value == _Annotations.Protected.value:
            # The "protected" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(context, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "visibility-enabled")
            if context._visibility[1] and context._visibility[0] != AstVisibility.Protected:
                raise SemanticErrors.AnnotationConflictError().add(self.name, context._visibility[1].name)
            context._visibility = (AstVisibility.Protected, self)

        elif self.name.value == _Annotations.Private.value:
            # The "private" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(context, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "visibility-enabled")
            if context._visibility[1] and context._visibility[0] != AstVisibility.Private:
                raise SemanticErrors.AnnotationConflictError().add(self.name, context._visibility[1].name)
            context._visibility = (AstVisibility.Private, self)

        elif self.name.value == _Annotations.Hidden.value:
            # The "hidden" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(context, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "visibility-enabled")
            if context._visibility[1] and context._visibility[0] != AstVisibility.Hidden:
                raise SemanticErrors.AnnotationConflictError().add(self.name, context._visibility[1].name)
            context._visibility = (AstVisibility.Hidden, self)

        elif self.name.value == _Annotations.Cold.value:
            # The "cold" annotation can only be applied to functions.
            if not isinstance(context, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "function")
            if context._hot:
                raise SemanticErrors.AnnotationConflictError().add(self.name, context._hot.name)
            context._cold = self

        elif self.name.value == _Annotations.Hot.value:
            # The "hot" annotation can only be applied to functions.
            if not isinstance(context, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, context.name, "function")
            if context._cold:
                raise SemanticErrors.AnnotationConflictError().add(self.name, context._cold.name)
            context._hot = self

        else:
            raise SemanticErrors.AnnotationInvalidError().add(self.name)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Prevent duplicate annotations from being applied to an AST.
        annotation_names = self._ctx.annotations.map_attr("name")
        if duplicate_annotations := annotation_names.filter(lambda a: a == self.name).remove(self.name):
            raise SemanticErrors.AnnotationDuplicateError().add(self.name, duplicate_annotations[0])


__all__ = ["AnnotationAst"]
