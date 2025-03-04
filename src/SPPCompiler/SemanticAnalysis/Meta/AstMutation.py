from __future__ import annotations

from typing import Callable


class AstMutation:
    @staticmethod
    def inject_code[T](code: str, parsing_function: Callable[..., T]) -> T:
        from SPPCompiler.LexicalAnalysis.Lexer import SppLexer
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser
        parser = SppParser(SppLexer(code + "\n").lex())
        return parser.parse_once(lambda: parsing_function(parser))
