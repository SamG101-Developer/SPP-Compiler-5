from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType


@dataclass
class Token:
    token_metadata: str
    token_type: TokenType

    def __str__(self):
        return self.token_metadata

    def __eq__(self, other: Token) -> bool:
        c1 = self.token_type == other.token_type
        c2 = self.token_metadata == other.token_metadata if self.token_type[:2] == "Lx" else True
        return c1 and c2


__all__ = ["Token"]
