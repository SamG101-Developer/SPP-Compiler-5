from __future__ import annotations

from typing import Iterable


class FastOrderedSet[T]:
    __slots__ = ("_data",)

    _data: dict[T, None]

    def __init__(self, iterable: Iterable[T] = ()) -> None:
        self._data = {item: None for item in iterable}

    def __sub__(self, other: FastOrderedSet[T]) -> FastOrderedSet[T]:
        return FastOrderedSet(item for item in self._data if item not in other._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item: T) -> bool:
        return item in self._data

    def pop(self, i: int) -> T:
        item = list(self._data.keys())[i]
        del self._data[item]
        return item


__all__ = [
    "FastOrderedSet"
]
