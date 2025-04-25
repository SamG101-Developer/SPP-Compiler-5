from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self, Optional, Tuple, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True)
class AbstractTypeTemporaryAst(ABC):
    """
    The AbstractTypeTemporaryAst is a temporary type ast that is used or instant-conversion purposes. The ast that it is
    inherited by will only be created for conversion purposes, ie shorthand type syntax.
    """

    @abstractmethod
    def convert(self) -> Asts.TypeAst:
        """
        This method allows conversion of temporarily created TypeAsts, to reduce the amount of analysing for different
        type asts. For example, "(Bool, Bool)" is converted into "Tup[Bool, Bool]" before it is ever analysed. All type
        shorthands implement and use this method.

        :return: The converted type ast.
        """


@dataclass(slots=True)
class AbstractTypeAst(AbstractTypeTemporaryAst):
    """
    The AbstractTypeAst contains a number of methods required to be implemented by all the different TypeAst classes.
    This allows for any of the Unary/Postfix/Single types to be used for any TypeAst value, with a common interface for
    all utility methods.
    """

    @abstractmethod
    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        """
        The type parts of a TypeAst are all the parts of the type asts that are not namespaces. For example, given
        "ns1::ns2::Type1::Type2", the type parts are "Type1" and "Type2".

        :return: The type parts of the type ast.
        """

    def namespace_parts(self) -> Seq[Asts.IdentifierAst]:
        """
        The namespace parts of a TypeAst are all the parts of the type asts that are namespaces. For example, given
        "ns1::ns2::Type1::Type2", the namespace parts are "ns1" and "ns2".

        :return: The namespace parts of the type ast.
        """
        return self.fq_type_parts().filter(lambda x: isinstance(x, Asts.IdentifierAst))

    @abstractmethod
    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        """
        The fully qualified type parts of a TypeAst are all the parts of the type asts that are namespace or type parts.
        For example, given "ns1::ns2::Type1::Type2", the fq type parts are "ns1", "ns2", "Type1" and "Type2".

        :return: The fully qualified type parts of the type ast.
        """

    @abstractmethod
    def without_generics(self) -> Self:
        """
        Create a new instance of ehte type asts that has had its generics removed. This is used especially for checking
        if types exist or need to be specialised. For example, "Vec[T]" becomes "Vec" when the generics are removed.

        :return: The type ast without generics.
        """

    @abstractmethod
    def substituted_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        """
        Substitute the generic arguments in a type. This allows "Vec[T]" to become "Vec[Str]" when it is known that "T"
        is a "Str". This is used in the type inference process. This creates a new type ast with the generics
        substituted, and returns the new type ast.

        :param generic_arguments: The generic arguments to substitute into the type.
        :return: The new type ast with the generic arguments substituted.
        """

    @abstractmethod
    def get_corresponding_generic(self, that: Asts.TypeAst, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        """
        Given this type is Vec[Opt[T]], getting the T type from Vec[Opt[Str]] will get T=Str.

        :param that:
        :param generic_name:
        :return:
        """

    @abstractmethod
    def contains_generic(self, generic_type: Asts.TypeSingleAst) -> bool:
        """
        Check recursively in this type, and its generic arguments, if the generic target type exists as a generic
        argument to a generic parameter. This is used to check that superimposition generics are constrained, and
        therefore inferrable, inside the "sup" block.

        :param generic_type: The target name to search for.
        :return: If the generic is contained by this type.
        """

    @abstractmethod
    def symbolic_eq(
            self, that: Asts.TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True,
            debug: bool = False) -> bool:
        """
        Symbolic equality is the core of the type checking utility. It gets two given types, and two scopes, and gets
        the symbols representing the types from the respective scopes. If the two symbol's types match, then the types
        are a match.

        :param that: The type (ast) to compare against.
        :param self_scope: The scope to get the symbol for this type.
        :param that_scope: The scope to get the symbol for the other type.
        :param check_variant: Check the internal types (if this type is a std::Var[..]).
        :param debug: Flag to optionally print debug information.
        :return: True if the types are equal, False otherwise.
        """

    @abstractmethod
    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        """
        Split a type ast, and a given scope into a new scope and type ast. This allows for "number::BigInt", in the
        scope "std", to be split into "std::number" and "BigInt".

        :param scope: The scope to split the type ast into.
        :return: A tuple containing the new scope and the type ast.
        """

    @abstractmethod
    def get_convention(self) -> Optional[Asts.ConventionAst]:
        """
        Get the convention attached to a type. This will either be "&" or "&mut", and the AST will only ever be part of
        a TypeUnaryExpressionAst.

        :return: The convention attached to the type, or None if no convention is attached.
        """

    def with_convention(self, convention: Optional[Asts.ConventionAst]) -> Asts.TypeAst:
        """
        Create a new instance of a type (that contains this original type), which acts as a unary type wrapper, with the
        given convention. This is used to attach conventions to types, for example, "&T".

        :param convention: The convention to attach to the type.
        :return: The new type ast with the attached convention.
        """

        if convention is None:
            return self

        if isinstance(self, Asts.TypeUnaryExpressionAst) and isinstance(self.op, Asts.TypeUnaryOperatorBorrowAst):
            self.op.convention = convention
            return self

        else:
            return Asts.TypeUnaryExpressionAst(pos=self.pos, op=Asts.TypeUnaryOperatorBorrowAst(pos=self.pos, convention=convention), rhs=self)

    @abstractmethod
    def without_conventions(self) -> Asts.TypeAst:
        """
        Get this type without its associated convention, if it exists. This is used to remove the convention from a type
        when it is no longer needed.

        :return: The type ast without the convention.
        """


__all__ = [
    "AbstractTypeAst",
    "AbstractTypeTemporaryAst"]
