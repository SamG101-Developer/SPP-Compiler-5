from dataclasses import dataclass, field


@dataclass
class Ordered:
    _variant: str = field(init=False, repr=False)


__all__ = ["Ordered"]
