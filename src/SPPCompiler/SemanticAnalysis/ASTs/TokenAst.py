from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class TokenAst(Ast):
    token_type: SppTokenType = field(default=None)
    token_data: str = field(default="")

    def __post_init__(self) -> None:
        assert self.token_type

    @staticmethod
    def raw(*, pos: int = -1, token_type: SppTokenType = SppTokenType.NoToken, token_metadata: str = "") -> TokenAst:
        return TokenAst(pos, token_type, token_metadata or token_type.value)

    def __eq__(self, other: TokenAst) -> bool:
        # Check both ASTs are the same type and have the same token.
        return isinstance(other, TokenAst) and self.token_type == other.token_type

    def __hash__(self) -> int:
        # Hash the token type's name into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5(self.token_type.name.encode()).digest())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.token_data


__all__ = ["TokenAst"]
