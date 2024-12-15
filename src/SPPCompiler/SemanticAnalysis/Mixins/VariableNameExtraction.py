from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import functools

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class VariableNameExtraction:
    _new_asts: dict = field(default_factory=dict, init=False)

    @functools.cached_property
    def extract_names(self) -> Seq[IdentifierAst]:
        raise

    @functools.cached_property
    def extract_name(self) -> IdentifierAst:
        raise
