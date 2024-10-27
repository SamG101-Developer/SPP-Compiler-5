from abc import ABC
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


@dataclass
class VisibilityEnabled(ABC):
    _visibility: AstVisibility = field(default=AstVisibility.Private, init=False)


# Decorator to apply the VisibilityEnabled class to a class.
def visibility_enabled_ast(cls: type) -> type:
    if VisibilityEnabled not in cls.__bases__:
        cls.__bases__ = (VisibilityEnabled,) + cls.__bases__
    return cls
