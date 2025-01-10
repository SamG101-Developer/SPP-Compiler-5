from __future__ import annotations
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SyntacticAnalysis.Parser import ParserRuleHandler


class AstMutation:
    @staticmethod
    def inject_code[T](code: str, parsing_function: Callable[..., ParserRuleHandler[T]]) -> T:
        from SPPCompiler.LexicalAnalysis.Lexer import SppLexer
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser
        return parsing_function(SppParser(SppLexer(code + "\n").lex())).parse_once()  # Todo: parse an <EOF> after
