from __future__ import annotations

from SParLex.Lexer.Lexer import Lexer
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType


class SppLexer(Lexer):
    def __init__(self, code: str) -> None:
        super().__init__(code, SppTokenType)


__all__ = ["SppLexer"]
