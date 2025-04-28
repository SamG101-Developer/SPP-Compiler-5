from __future__ import annotations

from typing import List

from SPPCompiler.LexicalAnalysis.TokenType import RawToken, RawTokenType


class Lexer:
    """
    The Lexer translates a string of code into a list of tokens. Only single-length tokens are created in the lexer,
    and the parser checks for multi-length tokens.

    Single line comments and string characters are supported by tracking starting and terminating boundary characters.
    Unknown tokens aren't errored, but are stored as an "unknown" token, so the parser can through a syntax error using
    an error formatter.
    """

    _code: str

    def __init__(self, code: str) -> None:
        # Add a newline to the start, so error-formatters can get the start of the 1st line of code if necessary.
        self._code = "\n" + code

    def lex(self) -> List[RawToken]:
        """
        Lex the code with single-character comparisons. Track strings and comments to skip and add characters as
        necessary.

        :return: A list of tokens.
        """

        tokens = []
        in_string = False
        in_single_line_comment = False

        for c in self._code:
            # Any character inside a token is skipped.
            if in_single_line_comment and c != "\n":
                continue

            # Any character inside speech marks is added as a character token.
            if in_string and c != '"':
                tokens.append(RawToken(RawTokenType.TkCharacter, c))
                continue

            # Match the character to a token type.
            match c:
                case _ if 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122:
                    tokens.append(RawToken(RawTokenType.TkCharacter, c))
                case _ if 48 <= ord(c) <= 57:
                    tokens.append(RawToken(RawTokenType.TkDigit, c))
                case "#":
                    in_single_line_comment = True
                    continue
                case "=":
                    tokens.append(RawToken(RawTokenType.TkEqualsSign, c))
                case "+":
                    tokens.append(RawToken(RawTokenType.TkPlusSign, c))
                case "-":
                    tokens.append(RawToken(RawTokenType.TkMinusSign, c))
                case "*":
                    tokens.append(RawToken(RawTokenType.TkAsterisk, c))
                case "/":
                    tokens.append(RawToken(RawTokenType.TkForwardSlash, c))
                case "%":
                    tokens.append(RawToken(RawTokenType.TkPercentSign, c))
                case "^":
                    tokens.append(RawToken(RawTokenType.TkCaret, c))
                case "<":
                    tokens.append(RawToken(RawTokenType.TkLessThanSign, c))
                case ">":
                    tokens.append(RawToken(RawTokenType.TkGreaterThanSign, c))
                case "(":
                    tokens.append(RawToken(RawTokenType.TkLeftParenthesis, c))
                case ")":
                    tokens.append(RawToken(RawTokenType.TkRightParenthesis, c))
                case "[":
                    tokens.append(RawToken(RawTokenType.TkLeftSquareBracket, c))
                case "]":
                    tokens.append(RawToken(RawTokenType.TkRightSquareBracket, c))
                case "{":
                    tokens.append(RawToken(RawTokenType.TkLeftCurlyBrace, c))
                case "}":
                    tokens.append(RawToken(RawTokenType.TkRightCurlyBrace, c))
                case "?":
                    tokens.append(RawToken(RawTokenType.TkQuestionMark, c))
                case ":":
                    tokens.append(RawToken(RawTokenType.TkColon, c))
                case "&":
                    tokens.append(RawToken(RawTokenType.TkAmpersand, c))
                case "|":
                    tokens.append(RawToken(RawTokenType.TkVerticalBar, c))
                case ".":
                    tokens.append(RawToken(RawTokenType.TkDot, c))
                case ",":
                    tokens.append(RawToken(RawTokenType.TkComma, c))
                case "@":
                    tokens.append(RawToken(RawTokenType.TkAt, c))
                case "_":
                    tokens.append(RawToken(RawTokenType.TkUnderscore, c))
                case '"':
                    in_string = not in_string
                    tokens.append(RawToken(RawTokenType.TkSpeechMark, c))
                case "$":
                    tokens.append(RawToken(RawTokenType.TkDollar, c))
                case " ":
                    tokens.append(RawToken(RawTokenType.TkWhitespace, c))
                case "\n":
                    tokens.append(RawToken(RawTokenType.TkNewLine, c))
                    in_single_line_comment = False
                case "\r":
                    continue
                case _:
                    tokens.append(RawToken(RawTokenType.TkUnknown, c))

        # Add a final end-of-file token.
        tokens.append(RawToken(RawTokenType.EndOfFile, ""))
        return tokens


__all__ = ["Lexer"]
