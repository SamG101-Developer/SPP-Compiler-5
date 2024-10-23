from __future__ import annotations
from typing import List, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType
    from SPPCompiler.LexicalAnalysis.Token import Token


class Lexer:
    _raw_code: str
    _alpha_regex: re.Pattern
    _comment_lexemes: List[TokenType]
    _multi_line_comment_lexemes: List[TokenType]

    def __init__(self, raw_code: str) -> None:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType

        self._raw_code = raw_code
        self._alpha_regex = re.compile(r"[A-Za-z_]")
        self._comment_lexemes = [TokenType.CmLxSingleLineComment, TokenType.CmLxMultiLineComment]
        self._multi_line_comment_lexemes = [TokenType.LxMultiLineComment]

    def lex(self, code_injection: bool = False) -> List[Token]:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.LexicalAnalysis.Token import Token

        i = 0
        token_stream = []

        # The "$" is only allowed in code injection (from semantic analysis).
        all_tokens = TokenType.all_tokens()
        if not code_injection:
            all_tokens.remove(TokenType.TkDollar)

        while i < len(self._raw_code):
            for token in all_tokens:
                p = token.name[:2]

                # Keywords: Match the keyword, and check the next character isn't [A-Za-z_] (identifier).
                if p == "Kw":
                    u = i + len(token.value)
                    if self._raw_code[i:u] == token.value and not self._alpha_regex.match(self._raw_code[u]):
                        token_stream.append(Token(token.value, token))
                        i = u
                        break

                # Lexemes: Match a lexeme by attempting to get a regex match against the current code.
                elif p == "Cm" and (matched := token.value.match(self._raw_code[i:])):
                    token not in self._comment_lexemes and token_stream.append(Token(matched.group(), token))
                    token in self._multi_line_comment_lexemes and token_stream.extend([Token("\n", TokenType.TkNewLine)] * matched.group().count("\n"))
                    i += len(matched.group())
                    break

                # Tokens: Match the token and increment the counter by the length of the token.
                elif p == "Tk":
                    u = i + len(token.value)
                    if self._raw_code[i:u] == token.value:
                        token_stream.append(Token(token.value, token))
                        i = u
                        break

            else:
                token_stream.append(Token(self._raw_code[i], TokenType.ERR))
                i += 1

        token_stream.insert(0, Token("\n", TokenType.TkNewLine))
        token_stream.append(Token("<EOF>", TokenType.TkEOF))
        return token_stream


__all__ = ["Lexer"]
