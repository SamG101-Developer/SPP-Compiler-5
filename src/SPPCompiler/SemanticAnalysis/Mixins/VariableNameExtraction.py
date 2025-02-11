from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import functools

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class VariableNameExtraction:
    _new_asts: dict = field(default_factory=dict, init=False)

    @functools.cached_property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        raise

    @functools.cached_property
    def extract_name(self) -> Asts.IdentifierAst:
        raise
