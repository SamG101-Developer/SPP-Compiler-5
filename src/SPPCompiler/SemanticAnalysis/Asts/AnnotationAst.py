from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import VisibilityEnabledAst, Visibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors

"""
Todo - ideas:
- Allow all bocks (loop/case+branches/with) etc to have annotations
- @noinline, @hot, @cold for functions
- @likely, @unlikely, @fallthrough for case branches
- @unroll, @allow_infinite for loops => map to a special return type?
"""


# Todo: only allow @ffi in stub files.
class _Annotations(Enum):
    """
    The _Annotations class is used to define the possible annotations that can be applied to ASTs. As Custom annotations
    are not yet supported, the annotations are defined as an Enum.
    """

    VirtualMethod = "virtual_method"
    AbstractMethod = "abstract_method"
    FFI = "ffi"
    NoImpl = "no_impl"  # temporary
    Public = "public"
    Protected = "protected"
    Private = "private"
    Cold = "cold"
    Hot = "hot"
    CompilerBuiltin = "compiler_builtin"
    AlwaysInline = "always_inline"  # test
    Inline = "inline"  # test


@dataclass(slots=True, repr=False)
class AnnotationAst(Asts.Ast):
    """
    The AnnotationAst class is used to represent annotations applied to ASTs. Annotations alter the behaviour of an AST,
    but do not generate code. For example marking a method as ``virtual_method`` will trigger specific compiler
    behaviour, but will not generate any code.

    There are a small number of annotations that have specific placements, such as ``virtual_method`` or
    ``abstract_method`` only being applicable to methods, or ``hot`` only being applicable to functions.

    Example:

    .. code-block:: S++

        @hot
        fun function() -> Void { ... }

    Custom annotations will be supported in the future, either once the compiler is self-hosting (easier token injection
    and modification), or compile time functions are supported.
    """

    tok_at: Asts.TokenAst = field(default=None)
    """The ``@`` character that marks the annotation. This must be present for each individual annotation."""

    name: Asts.IdentifierAst = field(default=None)
    """The name of the annotation."""

    def __post_init__(self) -> None:
        self.tok_at = self.tok_at or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAt)

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

    def pre_process(self, ctx: PreProcessingContext) -> None:
        """
        Mark the context AST with the correct attributes and values depending on the annotation. This allows all future
        compiler stages to utilize the additional behaviour based on the annotations.

        Most of the values set are setting this AST node itself as a flag (ie
        ``Asts.FunctionPrototypeAst._virtual = self``), but the visibility annotations also include the mapped
        ``Visibility``, so the mapping doesn't have to be recomputed per attribute access.

        :param ctx: The context AST to apply the annotation to.
        """

        # Import the necessary classes for type-comparisons to ensure annotation compatibility.
        Asts.Ast.pre_process(self, ctx)

        # Mark a method context as virtual.
        if self.name.value == _Annotations.VirtualMethod.value:
            ctx._virtual = self

        # Mark a method context as abstract.
        elif self.name.value == _Annotations.AbstractMethod.value:
            ctx._abstract = self

        # Mark a method context as non-implemented.
        elif self.name.value in [_Annotations.FFI.value, _Annotations.NoImpl.value, _Annotations.CompilerBuiltin.value]:
            ctx._non_implemented = self

        # Mark a context as public.
        elif self.name.value == _Annotations.Public.value:
            ctx._visibility = (Visibility.Public, self)

        # Mark a context as protected.
        elif self.name.value == _Annotations.Protected.value:
            ctx._visibility = (Visibility.Protected, self)

        # Mark a context as private.
        elif self.name.value == _Annotations.Private.value:
            ctx._visibility = (Visibility.Private, self)

        # Mark a function context as cold.
        elif self.name.value == _Annotations.Cold.value:
            ctx._cold = self

        # Mark a function context as hot.
        elif self.name.value == _Annotations.Hot.value:
            ctx._hot = self

        # Todo: LLVM attributes (@always_inline, @inline) and other compiler specific annotations.

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        """
        All annotation context checks, conflict checks, and validity checks are performed at this stage. They require
        a scope manager for error messages, so can't be performed at the ``pre_process`` stage. Although this stage of
        the compiler is typically used for generating a top level scope for a function or class, it is just utilized as
        an annotation analysis method that happens with scope access.

        It cannot be done in the analyse_semantics stage, because certain checks must happen before the behaviour based
        of annotations is utilized. For example, if both ``virtual_method`` and ``abstract_method`` were applied, their
        behaviour may both be applied in an inheritance analysis before these annotations were checked and found to be
        invalid.

        :param sm: The scope manager.
        :raise SemanticErrors.AnnotationInvalidLocationError: This exception is thrown if an annotation is applied to an
            invalid context. For example, applying ``virtual_method`` to a free function, or ``hot`` to a class.
        :raise SemanticErrors.AnnotationConflictError: This exception is raised if the annotation conflicts with another
            annotation; an example would be both ``hot`` and ``cold`` being applied to a function.
        :raise SemanticErrors.AnnotationInvalidError: This exception is thrown if the annotation is unknown. In future
            versions of the compiler, custom annotations will be supported.
        """

        # Import the necessary classes for type-comparisons to ensure annotation compatibility.
        Asts.Ast.generate_top_level_scopes(self, sm)

        if self.name.value == _Annotations.VirtualMethod.value:
            # The "virtual_method" annotation can only be applied to function asts.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-function").scopes(self._scope)

            # The function ast must be a class method, not a free function.
            if type(self._ctx._ctx) is Asts.ModulePrototypeAst:
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-class-method").scopes(self._scope)

            # The "virtual_method" annotation cannot be applied to an "abstract_method" annotation.
            if (c := self._ctx._abstract or self._ctx._virtual) and c is not self:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, (self._ctx._abstract or self._ctx._virtual).name).scopes(self._scope)

        elif self.name.value == _Annotations.AbstractMethod.value:
            # The "abstract_method" annotation can only be applied to function asts.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-function").scopes(self._scope)

            # The function ast must be a class method, not a free function.
            if type(self._ctx._ctx) is Asts.ModulePrototypeAst:
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-class-method").scopes(self._scope)

            # The "abstract_method" annotation cannot be applied to a "virtual_method" annotation.
            if (c := self._ctx._virtual or self._ctx._abstract) and c is not self:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, (self._ctx._virtual or self._ctx._abstract).name).scopes(self._scope)

        elif self.name.value in [_Annotations.FFI.value, _Annotations.NoImpl.value, _Annotations.CompilerBuiltin.value]:
            # The "ffi/no_impl/compiler_builtin" annotation can only be applied to functions.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-function").scopes(self._scope)

            # Neither of these can be applied to each other.
            if (c := self._ctx._non_implemented) and c is not self:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, self._ctx._non_implemented.name).scopes(self._scope)

        elif self.name.value in [_Annotations.Public.value, _Annotations.Protected.value, _Annotations.Private.value]:
            # Access modifier annotations can only be applied to visibility enabled objects.
            if not isinstance(self._ctx, VisibilityEnabledAst):
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-visibility-enabled").scopes(self._scope)

            # Access modifiers cannot be applied to methods in sup-ext blocks (only in module or sup).
            if type(self._ctx._ctx) is Asts.SupPrototypeExtensionAst and not self._ctx.name.value[0] == "$":
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx._ctx.name, "extension").scopes(self._scope)

            # There cannot be any other access modifier annotations applied to the object.
            if (c := self._ctx._visibility[1]) and c is not self:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, self._ctx._visibility[1].name).scopes(self._scope)

        elif self.name.value == _Annotations.Cold.value:
            # The "cold" annotation can only be applied to functions.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-function").scopes(self._scope)

            # There cannot be any other heat annotations applied to the object.
            if (c := self._ctx._hot or self._ctx._cold) and c is not self:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, (self._ctx._hot or self._ctx._cold).name).scopes(self._scope)

        elif self.name.value == _Annotations.Hot.value:
            # The "hot" annotation can only be applied to functions.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-function").scopes(self._scope)

            # There cannot be any other heat annotations applied to the object.
            if (c := self._ctx._cold or self._ctx._hot) and c is not self:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, (self._ctx._cold or self._ctx._hot).name).scopes(self._scope)

        elif self.name.value in [_Annotations.AlwaysInline.value, _Annotations.Inline.value]:
            # The "always_inline" and "inline" annotations can only be applied to functions.
            if not isinstance(self._ctx, Asts.FunctionPrototypeAst):
                raise SemanticErrors.AnnotationInvalidLocationError().add(
                    self.name, self._ctx.name, "non-function").scopes(self._scope)

            # There cannot be any other inline annotations applied to the object.
            if (c := self._ctx._inline) and c is not self:
                raise SemanticErrors.AnnotationConflictError().add(
                    self.name, self._ctx._inline.name).scopes(self._scope)

        else:
            # Unknown annotations are not allowed.
            raise SemanticErrors.AnnotationInvalidError().add(
                self.name).scopes(self._scope)


__all__ = [
    "AnnotationAst"]
