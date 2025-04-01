from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self, Optional, Tuple, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class AbstractTypeTemporaryAst(ABC):
    """!
    The AbstractTypeTemporaryAst is a temporary type ast that is used or instant-conversion purposes. The ast that it is
    inherited by will only be created for conversion purposes.
    """

    @abstractmethod
    def convert(self) -> Asts.TypeAst:
        """!
        This method allows conversion of temporarily created TypeAsts, to reduce the amount of analysing for different
        type asts. For example, "(Bool, Bool)" is converted into "Tup[Bool, Bool]" before it is ever analysed. All type
        shorthands implement and use this method.
        """


@dataclass
class AbstractTypeAst(AbstractTypeTemporaryAst):
    """!
    The AbstractTypeAst contains a number of methods required to be implemented by all the different TypeAst classes.
    This allows for any of the Unary/Postfix/Single types to be used for any TypeAst value, with a common interface for
    all utility methods.
    """

    @abstractmethod
    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        """!
        The type parts of a TypeAst are all the parts of the type asts that are not namespaces. For example, given
        "ns1::ns2::Type1::Type2", the type parts are "Type1" and "Type2".
        @return The type parts of the type ast.
        """

    def namespace_parts(self) -> Seq[Asts.IdentifierAst]:
        """!
        The namespace parts of a TypeAst are all the parts of the type asts that are namespaces. For example, given
        "ns1::ns2::Type1::Type2", the namespace parts are "ns1" and "ns2".
        @return The namespace parts of the type ast.
        """
        return self.fq_type_parts().filter(lambda x: isinstance(x, Asts.IdentifierAst))

    @abstractmethod
    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        """!
        The fully qualified type parts of a TypeAst are all the parts of the type asts that are namespace or type parts.
        For example, given "ns1::ns2::Type1::Type2", the fq type parts are "ns1", "ns2", "Type1" and "Type2".
        @return The namespace and type parts of the type ast.
        """

    @abstractmethod
    def without_generics(self) -> Self:
        """!
        Create a new instance of ehte type asts that has had its generics removed. This is used especially for checking
        if types exist or need to be specialised.
        @return The type ast with generics removed.
        """

    @abstractmethod
    def sub_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Self:
        """!
        Substitute the generic arguments in a type. This allows "Vec[T]" to become "Vec[Str]" when it is known that "T"
        is a "Str". This is used in the type inference process.
        @param generic_arguments The generic arguments to substitute into the type.
        @return The type ast with the generic arguments substituted.
        """

    @abstractmethod
    def get_generic(self, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        """!
        Get the generic argument for a given generic parameter name. This is defined as a method because unary type
        expressions needs to more through their namespace parts first (can't always access the actual type directly).
        @param generic_name The name of the generic parameter to get.
        @return The type ast of the generic argument, or None if the generic parameter is not found.
        """

    @abstractmethod
    def get_generic_parameter_for_argument(self, argument: Asts.TypeAst) -> Optional[Asts.TypeAst]:
        """!
        Given a generic argument, get the first parameter whose name matches the argument. This is used for nested
        generic inference, todo.
        """

    @abstractmethod
    def contains_generic(self, generic_name: Asts.TypeSingleAst) -> bool:
        """!
        Check if a type contains a specific generic parameter name. This is defined as a method for the same reason that
        get_generic() is.
        @param generic_name The name of the generic parameter to check for.
        @return True if the generic parameter is found, False otherwise.
        """

    @abstractmethod
    def symbolic_eq(
            self, that: Asts.TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True,
            debug: bool = False) -> bool:
        """!
        Symbolic equality is the core of the type checking utility. It gets two given types, and two scopes, and gets
        the symbols representing the types, from the respective scopes. If the two symbol's types match, then the types
        are a match.
        @param that The type (ast) to compare against.
        @param self_scope The scope to get the symbol for this type.
        @param that_scope The scope to get the symbol for the other type.
        @param check_variant Check the internal types (if this type is a std::Var[..]).
        @param debug Print debug information.
        @return True if the types are equal, False otherwise.
        """

    @abstractmethod
    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        """!
        Split a type ast, and a given scope into a new scope and type ast. This allows for "number::BigInt", in the
        scope "std", to be split into "std::number" and "BigInt".
        @param scope The scope to split the type ast into.
        @return A tuple containing the new scope and the type ast.
        """

    @abstractmethod
    def get_conventions(self) -> Seq[Asts.ConventionAst]:
        """!
        Get the convention attached to a type.
        @return The convention attached to the type, or None if no convention is attached.
        """

    def with_conventions(self, conventions: Seq[Asts.ConventionAst]) -> Asts.TypeAst:
        """!
        Create a new instance of a type (that contains this original type), which acts as a unary type wrapper, with the
        given convention. This is used to attach conventions to types, for example, "&T".
        @param convention The convention to attach to the type.
        @return The new type ast with the attached convention.
        """

        if conventions.is_empty():
            return self

        main_type = self
        for c in conventions.reverse():
            main_type = Asts.TypeUnaryExpressionAst(
                pos=main_type.pos, op=Asts.TypeUnaryOperatorBorrowAst(pos=main_type.pos, convention=c), rhs=main_type)
        return main_type

    @abstractmethod
    def without_conventions(self) -> Asts.TypeAst:
        """!
        Get this type without its associated convention, if it exists. This is used to remove the convention from a type
        when it is no longer needed.
        @return The type ast without the convention.
        """


__all__ = [
    "AbstractTypeAst",
    "AbstractTypeTemporaryAst"]
