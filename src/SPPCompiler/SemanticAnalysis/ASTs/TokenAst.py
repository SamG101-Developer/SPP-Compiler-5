from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import hashlib

from SParLex.Lexer.Tokens import SpecialToken

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType


@dataclass
class TokenAst(Ast, Default, CompilerStages):
    token: Token

    def __eq__(self, other: TokenAst) -> bool:
        # Check both ASTs are the same type and have the same token.
        return isinstance(other, TokenAst) and self.token == other.token

    def __hash__(self) -> int:
        # Hash the token type's name into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5(self.token.token_type.name.encode()).digest())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.token.token_metadata

    @staticmethod
    def default(token_type: SppTokenType = SpecialToken.NO_TOK, info: str = "", pos: int = -1) -> TokenAst:
        return TokenAst(pos, Token(info or token_type.value, token_type))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Required for ".." being used as an expression in binary folding.
        pass


__all__ = ["TokenAst"]
