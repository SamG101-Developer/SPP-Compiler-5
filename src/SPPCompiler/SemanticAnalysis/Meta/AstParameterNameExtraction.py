from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING
import functools

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class AstParameterNameExtraction(ABC):
    @functools.cached_property
    def extract_names(self) -> Seq:
        from SPPCompiler.SemanticAnalysis import LocalVariableSingleIdentifierAst

        # Todo: Move to extracting all names from nested local variable asts when support is added
        match self.variable:
            case LocalVariableSingleIdentifierAst(): return Seq([self.variable.name])
            case _: return Seq([IdentifierAst(self.variable.pos, "UNMATCHABLE")])
