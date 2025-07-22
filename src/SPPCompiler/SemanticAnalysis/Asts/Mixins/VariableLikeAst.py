from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Final

from SPPCompiler.SemanticAnalysis import Asts


@dataclass
class VariableLikeAst:
    UNMATCHABLE_VARIABLE: Final[str] = field(default="_UNMATCHABLE", init=False, repr=False)

    """!
    A VariableLikeAst is an AST that is either a variable, or treated as one. This is limited to the LocalVariableXXX
    and FunctionParameterXXX classes, and provides a way to extract the named information from them. This allows for
    destructured named to be returned where required.
    """

    _from_pattern: bool = field(default=False, init=False, repr=False)

    @property
    @abstractmethod
    def extract_names(self) -> list[Asts.IdentifierAst]:
        """!
        Extract the names represented by this AST. For "let (x, y) = 123", "(x, y)" is the local variables, and its
        names are "x" and "y". Nested destructuring is supposed, so this method will be recursive.
        @return The list of names.
        """

    @property
    @abstractmethod
    def extract_name(self) -> Asts.IdentifierAst:
        """!
        Extract the single name, if possible, represented by this AST for "f(a: Str)", "a: Str" is the function
        parameter, and its name is "a". When a destructure is used, there is no single name, so the placeholder
        "UNMATCHABLE_VARIABLE" is used.
        """


__all__ = [
    "VariableLikeAst"]
