from __future__ import annotations
from dataclasses import dataclass
import hashlib

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class TokenAst(Ast, Default):
    token: Token

    def __eq__(self, other: TokenAst) -> bool:
        return isinstance(other, TokenAst) and self.token == other.token

    def __hash__(self) -> int:
        return int.from_bytes(hashlib.md5(self.token.token_type.name.encode()).digest())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.token.token_metadata

    @staticmethod
    def default(token_type: TokenType = TokenType.NO_TOK, info: str = "", pos: int = -1) -> TokenAst:
        return TokenAst(pos, Token(info or token_type.value, token_type))


__all__ = ["TokenAst"]
