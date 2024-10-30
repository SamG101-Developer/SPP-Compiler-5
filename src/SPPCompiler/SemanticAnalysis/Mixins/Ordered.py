from abc import ABC
from dataclasses import dataclass, field


@dataclass
class Ordered(ABC):
    _variant: str = field(init=False, repr=False)


__all__ = ["Ordered"]
