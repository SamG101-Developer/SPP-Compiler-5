from dataclasses import dataclass, field
from fastenum import Enum
from typing import Optional, Tuple

from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst


class AstVisibility(Enum):
    Public = 0
    Protected = 1
    Private = 2
    Hidden = 3

    def __str__(self) -> str:
        return self.name.lower()

    def __json__(self) -> str:
        return self.name.lower()


@dataclass
class VisibilityEnabled:
    _visibility: Tuple[AstVisibility, Optional[AnnotationAst]] = field(default=(AstVisibility.Private, None), kw_only=True, repr=False)
