from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled, AstVisibility
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

"""
Todo - ideas:
- Allow all bocks (loop/case+branches/with) etc to have annotations
- @inline, @noinline, @hot, @cold for functions
- @likely, @unlikely, @fallthrough for case branches
- @unroll, @allow_infinite for loops => map to a special return type?
"""


class _Annotations(Enum):
    """!
    The _Annotations class is used to define the possible annotations that can be applied to ASTs. As Custom annotations
    are not yet supported, the annotations are defined as an Enum.
    """

    VirtualMethod = "virtual_method"
    AbstractMethod = "abstract_method"
    NonImplementedMethod = "no_impl"
    Public = "public"
    Protected = "protected"
    Private = "private"
    Hidden = "hidden"
    Cold = "cold"
    Hot = "hot"
    CompilerBuiltin = "compiler_builtin"


@dataclass
class AnnotationAst(Ast):
    """!
    The AnnotationAst class is used to represent annotations applied to ASTs. Annotations alter the behaviour of an AST,
    but do not generate code. For example marking a method as "virtual_method" will trigger specific compiler behaviour,
    but will not generate any code.
    """

    tok_at: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAt))
    name: Asts.IdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name

    def __deepcopy__(self, memodict: Dict = None) -> AnnotationAst:
        # Create a deep copy of the AST.
        return AnnotationAst(self.pos, self.tok_at, self.name, _ctx=self._ctx)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_at.print(printer),
            self.name.print(printer) + " "]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    def pre_process(self, context: PreProcessingContext) -> None:
        # Import the necessary classes for type-comparisons to ensure annotation compatibility.
        super().pre_process(context)

        if self.name.value == _Annotations.VirtualMethod.value:
            context._virtual = self

        elif self.name.value == _Annotations.AbstractMethod.value:
            context._abstract = self

        elif self.name.value in [_Annotations.NonImplementedMethod.value, _Annotations.CompilerBuiltin.value]:
            context._non_implemented = self

        elif self.name.value == _Annotations.Public.value:
            context._visibility = (AstVisibility.Public, self)

        elif self.name.value == _Annotations.Protected.value:
            context._visibility = (AstVisibility.Protected, self)

        elif self.name.value == _Annotations.Private.value:
            context._visibility = (AstVisibility.Private, self)

        elif self.name.value == _Annotations.Hidden.value:
            context._visibility = (AstVisibility.Hidden, self)

        elif self.name.value == _Annotations.Cold.value:
            context._cold = self

        elif self.name.value == _Annotations.Hot.value:
            context._hot = self

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Import the necessary classes for type-comparisons to ensure annotation compatibility.
        super().generate_top_level_scopes(scope_manager)

        if self.name.value == _Annotations.VirtualMethod.value:
            # The "virtual_method" annotation can only be applied to function asts.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "function").scopes(self._scope)

            # The function ast must be a class method, not a free function.
            if isinstance(self._ctx._ctx, Asts.ModulePrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "class-method").scopes(self._scope)

            # The "virtual_method" annotation cannot be applied to an "abstract_method" annotation.
            if self._ctx._abstract:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._abstract.name).scopes(self._scope)

        elif self.name.value == _Annotations.AbstractMethod.value:
            # The "abstract_method" annotation can only be applied to function asts.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "function").scopes(self._scope)

            # The function ast must be a class method, not a free function.
            if isinstance(self._ctx._ctx, Asts.ModulePrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "class-method").scopes(self._scope)

            # The "abstract_method" annotation cannot be applied to a "virtual_method" annotation.
            if self._ctx._virtual:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._virtual.name).scopes(self._scope)

        elif self.name.value in [_Annotations.NonImplementedMethod.value, _Annotations.CompilerBuiltin.value]:
            # The "non_implemented_method" annotation can only be applied to functions.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "function").scopes(self._scope)

        elif self.name.value == _Annotations.Public.value:
            # The "public" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(self._ctx, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "visibility-enabled").scopes(self._scope)

            # There cannot be any other access modifier annotations applied to the object.
            if self._ctx._visibility[1] and self._ctx._visibility[0] != AstVisibility.Public:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._visibility[1].name).scopes(self._scope)

        elif self.name.value == _Annotations.Protected.value:
            # The "protected" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(self._ctx, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "visibility-enabled").scopes(self._scope)

            # There cannot be any other access modifier annotations applied to the object.
            if self._ctx._visibility[1] and self._ctx._visibility[0] != AstVisibility.Protected:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._visibility[1].name).scopes(self._scope)

        elif self.name.value == _Annotations.Private.value:
            # The "private" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(self._ctx, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "visibility-enabled").scopes(self._scope)

            # There cannot be any other access modifier annotations applied to the object.
            if self._ctx._visibility[1] and self._ctx._visibility[0] != AstVisibility.Private:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._visibility[1].name).scopes(self._scope)

        elif self.name.value == _Annotations.Hidden.value:
            # The "hidden" access modifier annotation can only be applied to visibility enabled objects.
            if not isinstance(self._ctx, VisibilityEnabled):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "visibility-enabled").scopes(self._scope)

            # There cannot be any other access modifier annotations applied to the object.
            if self._ctx._visibility[1] and self._ctx._visibility[0] != AstVisibility.Hidden:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._visibility[1].name).scopes(self._scope)

        elif self.name.value == _Annotations.Cold.value:
            # The "cold" annotation can only be applied to functions.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "function").scopes(self._scope)

            # There cannot be any other access modifier annotations applied to the object.
            if self._ctx._hot:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._hot.name).scopes(self._scope)

        elif self.name.value == _Annotations.Hot.value:
            # The "hot" annotation can only be applied to functions.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidApplicationError().add(self.name, self._ctx.name, "function").scopes(self._scope)

            # There cannot be any other access modifier annotations applied to the object.
            if self._ctx._cold:
                raise SemanticErrors.AnnotationConflictError().add(self.name, self._ctx._cold.name).scopes(self._scope)

        else:
            raise SemanticErrors.AnnotationInvalidError().add(self.name).scopes(self._scope)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Prevent duplicate annotations from being applied to an AST.
        annotation_names = self._ctx.annotations.map_attr("name")
        if duplicate_annotations := annotation_names.filter(lambda a: a == self.name).remove(self.name):
            raise SemanticErrors.AnnotationDuplicateError().add(self.name, duplicate_annotations[0]).scopes(self._scope)


__all__ = ["AnnotationAst"]
