from __future__ import annotations

from abc import ABC, abstractmethod

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class TypeInferrable(ABC):
    """!
    The TypeInferrable class allows for the resulting type of evaluating the code that created an AST, to be determined.
    Every expression-based AST, and a few others, are type inferrable.
    """

    @abstractmethod
    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """!
        Given the AST, and the scope manager (with knowledge o the current scope etc), determine teh resulting type of
        this AST. A lot of ASTs will recursively call this method on their children for more type information.
        @param sm The scope manager.
        @param kwargs Additional keyword arguments.
        @return The resulting type of the AST.
        """


__all__ = [
    "TypeInferrable"]
