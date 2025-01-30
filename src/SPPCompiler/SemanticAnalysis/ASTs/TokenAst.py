from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import std
from SParLex.Lexer.Tokens import SpecialToken

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class TokenAst(Ast):
    token: Token = field(default=None)

    def __post_init__(self) -> None:
        assert self.token

    @staticmethod
    def raw(*, pos: int = -1, token: SppTokenType = SpecialToken.NO_TOK, token_metadata: str = "") -> TokenAst:
        from SPPCompiler.LexicalAnalysis.Token import Token
        return TokenAst(pos, Token(token_metadata or token.value, token))

    @std.override_method
    def __eq__(self, other: TokenAst) -> bool:
        # Check both ASTs are the same type and have the same token.
        return isinstance(other, TokenAst) and self.token == other.token

    @std.override_method
    def __hash__(self) -> int:
        # Hash the token type's name into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5(self.token.token_type.name.encode()).digest())

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        return self.token.token_metadata


__all__ = ["TokenAst"]
