from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import functools

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class VariableNameExtraction:
    @functools.cached_property
    def extract_names(self) -> Seq[IdentifierAst]:
        ...

    @functools.cached_property
    def extract_name(self) -> IdentifierAst:
        raise
