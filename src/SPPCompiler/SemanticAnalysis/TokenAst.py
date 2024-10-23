from __future__ import annotations
from dataclasses import dataclass
import hashlib

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default


@dataclass
class TokenAst(Ast, Default):
    token: Token

    @staticmethod
    def default(token_type: TokenType = TokenType.NO_TOK, info: str = "", pos: int = -1) -> TokenAst:
        return TokenAst(pos, Token(info, token_type))

    def __eq__(self, other: TokenAst) -> bool:
        return isinstance(other, TokenAst) and self.token == other.token

    def __hash__(self) -> int:
        return int.from_bytes(hashlib.md5(self.token.token_type.name.encode()).digest())


__all__ = ["TokenAst"]
