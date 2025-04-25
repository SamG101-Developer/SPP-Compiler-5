from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Optional, Tuple

from enum import Enum

from SPPCompiler.SemanticAnalysis import Asts


class Visibility(Enum):
    """!
    The Visibility enum is used to represent the visibility of an object. The visibility of an object can be one of the
    following:
    * Public: The object is visible to all other objects and modules.
    * Protected: The object is visible to the object itself and its subclasses.
    * Private: The object is visible only to the object itself and this module.
    """

    Public = 0
    Protected = 1
    Private = 2

    def __str__(self) -> str:
        """!
        The string representation of the visibility enum is the lowercase name of the enum.
        @return The lowercase name of the enum.
        """

        return self.name.lower()

    def __json__(self) -> str:
        """!
        The JSON representation of the visibility enum is the lowercase name of the enum.
        @return The lowercase name of the enum.
        """

        return self.name.lower()


type VisibilityPair = Tuple[Optional[Visibility], Optional[Asts.AnnotationAst]]


@dataclass
class VisibilityEnabledAst(ABC):
    """!
    Visibility enabled Asts contain an attribute pertaining to the visibility of the object. The visibility of an object
    is a pair of the type os visibility (from the enumeration), and the annotationAst that marked the visibility (for
    error printing if required).
    """

    _visibility: VisibilityPair = field(default=(Visibility.Private, None), kw_only=True, repr=False)


__all__ = [
    "VisibilityEnabledAst"]
