from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType


@dataclass
class Token:
    token_metadata: str
    token_type: TokenType

    def __str__(self) -> str:
        return self.token_metadata

    def __eq__(self, other: Token) -> bool:
        # Check both ASTs are the same type and have the same token type and metadata.
        c0 = isinstance(other, Token)
        if c0:
            c1 = self.token_type == other.token_type
            c2 = self.token_metadata == other.token_metadata if self.token_type.name[:2] in ["Lx", "Cm"] else True
            return c1 and c2
        return False


__all__ = ["Token"]
