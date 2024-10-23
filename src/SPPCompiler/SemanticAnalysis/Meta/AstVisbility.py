from dataclasses import dataclass, field
from fastenum import Enum


class AstVisibility(Enum):
    Public = 0
    Protected = 1
    Private = 2

    def __str__(self) -> str:
        return self.name.lower()

    def __json__(self) -> str:
        return self.name.lower()


class VisibilityEnabled:
    _visibility: AstVisibility = field(default=AstVisibility.Private, init=False)
