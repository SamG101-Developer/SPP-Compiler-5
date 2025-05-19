from __future__ import annotations

from abc import abstractmethod
from typing import List, Optional, TYPE_CHECKING, final

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True)
class AbstractTypeTemporaryAst:
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

    def type_parts(self) -> List[Asts.GenericIdentifierAst]:
        """
        The type parts of a TypeAst are all the parts of the type asts that are not namespaces. For example, given
        "ns1::ns2::Type1::Type2", the type parts are "Type1" and "Type2".

        :return: The type parts of the type ast.
        """

        return [p for p in self.fq_type_parts() if p.__class__ is Asts.GenericIdentifierAst]

    def namespace_parts(self) -> List[Asts.IdentifierAst]:
        """
        The namespace parts of a TypeAst are all the parts of the type asts that are namespaces. For example, given
        "ns1::ns2::Type1::Type2", the namespace parts are "ns1" and "ns2".

        :return: The namespace parts of the type ast.
        """

        return [p for p in self.fq_type_parts() if p.__class__ is Asts.IdentifierAst]

    @abstractmethod
    def fq_type_parts(self) -> List[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
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
    def substituted_generics(self, generic_arguments: List[Asts.GenericArgumentAst]) -> Asts.TypeAst:
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
    def get_symbol(self, scope: Scope) -> TypeSymbol:
        """
        Get the symbol for this type. This is used to get the symbol for the type in the current scope. Type unary
        expressions use their namespace to move into the type, and postfix types use the lhs types.

        :param scope: The scope to get the symbol from.
        :return: The type symbol for this type.
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
