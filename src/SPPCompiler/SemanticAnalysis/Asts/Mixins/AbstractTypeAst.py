from __future__ import annotations

import copy
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING, final

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


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


@dataclass()
class AbstractTypeAst(AbstractTypeTemporaryAst):
    """
    The AbstractTypeAst contains a number of methods required to be implemented by all the different TypeAst classes.
    This allows for any of the Unary/Postfix/Single types to be used for any TypeAst value, with a common interface for
    all utility methods.
    """

    @property
    @abstractmethod
    def fq_type_parts(self) -> List[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        ...

    @property
    @abstractmethod
    def without_generics(self) -> Optional[Asts.TypeAst]:
        ...

    @property
    @abstractmethod
    def without_conventions(self) -> Optional[Asts.TypeAst]:
        ...

    @property
    @abstractmethod
    def convention(self) -> Optional[Asts.ConventionAst]:
        ...

    @property
    def namespace_parts(self) -> List[Asts.IdentifierAst]:
        return [p for p in self.fq_type_parts if p.__class__ is Asts.IdentifierAst]

    @property
    def type_parts(self) -> List[Asts.GenericIdentifierAst | Asts.TokenAst]:
        return [p for p in self.fq_type_parts if p.__class__ is Asts.GenericIdentifierAst or p.__class__ is Asts.TokenAst]

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

    @final
    def set_generics(self, generics_argument_group: Asts.GenericArgumentGroupAst) -> Asts.TypeAst:
        new = copy.deepcopy(self)
        new.type_parts[-1].generic_argument_group = generics_argument_group
        return new

    @final
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


__all__ = [
    "AbstractTypeAst",
    "AbstractTypeTemporaryAst"]
