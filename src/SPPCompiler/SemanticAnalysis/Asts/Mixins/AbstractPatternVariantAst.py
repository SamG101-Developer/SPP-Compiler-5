from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import Asts


@dataclass
class AbstractPatternVariantAst(ABC):
    """!
    The AbstractPatternVariantAst class is a mixin that provides the ability to convert an instance of a pattern variant
    into a corresponding local variable declaration. This is because most of the patterns are mirrors of creating
    variables. For example, tuple-destructure patterns create a tuple value, so they are mapped into tuple-destructure
    variables, and analysed.
    """

    @abstractmethod
    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableAst:
        """!
        The convert_to_variable method is a method that converts the current pattern variant into a local variable
        declaration. This is useful for the semantic analysis phase, as it allows for the pattern to be analysed as a
        variable declaration, removing all code duplication.

        @return The local variable declaration that corresponds to the current pattern variant.
        """


__all__ = [
    "AbstractPatternVariantAst"]
