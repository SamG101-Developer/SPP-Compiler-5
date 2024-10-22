from __future__ import annotations
from ordered_set import OrderedSet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType


class ParserError(Exception):
    pos: int
    expected_tokens: OrderedSet[TokenType]

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.pos = -1
        self.expected_tokens = OrderedSet()


__all__ = ["ParserError"]
