from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, final

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache


class AbstractTypeTemporaryAst:
    """
    The AbstractTypeTemporaryAst is a temporary type ast that is used or instant-conversion purposes. The ast that it is
    inherited by will only be created for conversion purposes, ie shorthand type syntax.
    """

    def convert(self) -> Asts.TypeAst:
        """
        This method allows conversion of temporarily created TypeAsts, to reduce the amount of analysing for different
        type asts. For example, "(Bool, Bool)" is converted into "Tup[Bool, Bool]" before it is ever analysed. All type
        shorthands implement and use this method.
        """


@dataclass()
class AbstractTypeAst(AbstractTypeTemporaryAst):
    """
    The AbstractTypeAst contains a number of methods required to be implemented by all the different TypeAst classes.
    This allows for any of the Unary/Postfix/Single types to be used for any TypeAst value, with a common interface for
    all utility methods.
    """

    def is_never_type(self) -> bool:
        return False

    @property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst]:
        """
        The fully qualified type parts of the type. This extracts the IdentifierAst nodes and TypeIdentifierAst nodes
        that are part of the type. The fq_type_parts of "std::vector::Vec[T]::Element" would be ["std", "vector", "Vec",
        "Element"].
        """

        return []

    @property
    def namespace_parts(self) -> list[Asts.IdentifierAst]:
        """
        The namespace parts of the type. This extracts the IdentifierAst nodes preceding the TypeIdentifier for this
        type. The namespace parts of "std::vector::Vec[T]::Element" would be ["std", "vector"].
        """

        return []

    @property
    def type_parts(self) -> list[Asts.TypeIdentifierAst]:
        """
        The type parts of the type. This extracts the TypeIdentifierAst nodes that are part of the type. The type parts
        of "std::vector::Vec[T]::Element" would be ["Vec", "Element"].
        """

        return []

    @property
    def without_convention(self) -> Optional[Asts.TypeAst]:
        """
        Get the type without any convention. This is used to get the type without any convention, for example, "&T"
        would become "T".
        """

        return None

    @property
    def convention(self) -> Optional[Asts.ConventionAst]:
        """
        Get the convention of the type. This is gets th outer "borrow" convention ast if there is one present. For
        example, "&T" would return the "&" convention ast, while "T" would return "None".
        """

        return None

    @FunctionCache.cache_property
    def without_generics(self) -> Optional[Asts.TypeAst]:
        """
        Get the type without any generic arguments. This is used to get the type without any generic arguments, for
        example, "Vec[T]" would become "Vec". This is used in the type inference process to get the base type of a
        generic type.
        """

        return None

    def substituted_generics(self, generic_arguments: list[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        """
        Substitute the generic arguments in a type. This allows "Vec[T]" to become "Vec[Str]" when it is known that "T"
        is a "Str". This is used in the type inference process. This creates a new type ast with the generics
        substituted, and returns the new type ast.
        """

        return None

    def match_generic(self, that: Asts.TypeAst, generic_name: Asts.TypeIdentifierAst) -> Optional[Asts.TypeAst]:
        """
        Perform a deep search to match a generic fro the type (almost an inverse of the substitute generics; search
        rather than substitute). For example, when comparing "Vec[T]" with "Vec[Str]", looking for "T", "Str" would be
        returned. Types of varying generic depths are supported, which is key for advanced inference.
        """

        return None

    def contains_generic(self, generic_type: Asts.TypeIdentifierAst) -> bool:
        """
        Check recursively in this type, and its generic arguments, if the generic target type exists as a generic
        argument to a generic parameter. This is used to check that superimposition generics are constrained, and
        therefore inferrable, inside the "sup" block.
        """

        return False

    @final
    def with_generics(self: Asts.TypeAst, generics_argument_group: Asts.GenericArgumentGroupAst) -> Asts.TypeAst:
        """
        Directly set the generics argument group for this type. This doesn't use substitution, but rather "glues" the
        generics argument group to the type. This is used when the generics are already known to be valid.
        """

        new = fast_deepcopy(self)
        new.type_parts[-1].generic_argument_group = generics_argument_group
        return new

    @final
    def with_convention(self: Asts.TypeAst, convention: Optional[Asts.ConventionAst]) -> Asts.TypeAst:
        """
        Create a new instance of a type (that contains this original type), which acts as a unary type wrapper, with the
        given convention. This is used to attach conventions to types, for example, "&T".

        :param convention: The convention to attach to the type.
        :return: The new type ast with the attached convention.
        """

        if convention is None:
            return self

        if type(self) is Asts.TypeUnaryExpressionAst and type(self.op) is Asts.TypeUnaryOperatorBorrowAst:
            self.op.convention = convention
            return self

        else:
            return Asts.TypeUnaryExpressionAst(pos=self.pos, op=Asts.TypeUnaryOperatorBorrowAst(pos=self.pos, convention=convention), rhs=self)


__all__ = [
    "AbstractTypeAst",
    "AbstractTypeTemporaryAst"]
