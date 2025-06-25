from __future__ import annotations

from typing import List

from SPPCompiler.LexicalAnalysis.TokenType import RawKeywordType, RawToken, RawTokenType


def is_alphanumeric(c: str) -> bool:
    """
    Check if a character is alphanumeric (a-z, A-Z, 0-9).

    :param c: The character to check.
    :return: True if the character is alphanumeric, False otherwise.
    """
    return c.isalnum() or c == "_"


class SppLexer:
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

        i = 0
        while i < len(self._code):
            c = self._code[i]

            # Any character inside a token is skipped.
            if in_single_line_comment and c != "\n":
                i += 1
                continue

            # Any character inside speech marks is added as a character token.
            if in_string and c != '"':
                tokens.append(RawToken(RawTokenType.TkCharacter, c))
                i += 1
                continue

            # Match the character to a token type.
            match c:
                case "#":
                    in_single_line_comment = True
                    i += 1
                    continue
                case "=":
                    tokens.append(RawToken(RawTokenType.TkEqualsSign, c))
                    i += 1
                    continue
                case "+":
                    tokens.append(RawToken(RawTokenType.TkPlusSign, c))
                    i += 1
                    continue
                case "-":
                    tokens.append(RawToken(RawTokenType.TkMinusSign, c))
                    i += 1
                    continue
                case "*":
                    tokens.append(RawToken(RawTokenType.TkAsterisk, c))
                    i += 1
                    continue
                case "/":
                    tokens.append(RawToken(RawTokenType.TkForwardSlash, c))
                    i += 1
                    continue
                case "%":
                    tokens.append(RawToken(RawTokenType.TkPercentSign, c))
                    i += 1
                    continue
                case "^":
                    tokens.append(RawToken(RawTokenType.TkCaret, c))
                    i += 1
                    continue
                case "<":
                    tokens.append(RawToken(RawTokenType.TkLessThanSign, c))
                    i += 1
                    continue
                case ">":
                    tokens.append(RawToken(RawTokenType.TkGreaterThanSign, c))
                    i += 1
                    continue
                case "(":
                    tokens.append(RawToken(RawTokenType.TkLeftParenthesis, c))
                    i += 1
                    continue
                case ")":
                    tokens.append(RawToken(RawTokenType.TkRightParenthesis, c))
                    i += 1
                    continue
                case "[":
                    tokens.append(RawToken(RawTokenType.TkLeftSquareBracket, c))
                    i += 1
                    continue
                case "]":
                    tokens.append(RawToken(RawTokenType.TkRightSquareBracket, c))
                    i += 1
                    continue
                case "{":
                    tokens.append(RawToken(RawTokenType.TkLeftCurlyBrace, c))
                    i += 1
                    continue
                case "}":
                    tokens.append(RawToken(RawTokenType.TkRightCurlyBrace, c))
                    i += 1
                    continue
                case "?":
                    tokens.append(RawToken(RawTokenType.TkQuestionMark, c))
                    i += 1
                    continue
                case ":":
                    tokens.append(RawToken(RawTokenType.TkColon, c))
                    i += 1
                    continue
                case "&":
                    tokens.append(RawToken(RawTokenType.TkAmpersand, c))
                    i += 1
                    continue
                case "|":
                    tokens.append(RawToken(RawTokenType.TkVerticalBar, c))
                    i += 1
                    continue
                case ".":
                    tokens.append(RawToken(RawTokenType.TkDot, c))
                    i += 1
                    continue
                case ",":
                    tokens.append(RawToken(RawTokenType.TkComma, c))
                    i += 1
                    continue
                case "@":
                    tokens.append(RawToken(RawTokenType.TkAt, c))
                    i += 1
                    continue
                case "_":
                    tokens.append(RawToken(RawTokenType.TkUnderscore, c))
                    i += 1
                    continue
                case "!":
                    tokens.append(RawToken(RawTokenType.TkExclamationMark, c))
                    i += 1
                    continue
                case '"':
                    in_string = not in_string
                    tokens.append(RawToken(RawTokenType.TkSpeechMark, c))
                    i += 1
                    continue
                case "$":
                    tokens.append(RawToken(RawTokenType.TkDollar, c))
                    i += 1
                    continue
                case " ":
                    tokens.append(RawToken(RawTokenType.TkWhitespace, c))
                    i += 1
                    continue
                case "\n":
                    tokens.append(RawToken(RawTokenType.TkNewLine, c))
                    in_single_line_comment = False
                    i += 1
                    continue
                case "\r":
                    i += 1
                    continue

            kw = False
            for keyword in RawKeywordType:
                if self._code.startswith(keyword.value, i) and not (
                    (i > 0 and is_alphanumeric(self._code[i - 1])) or
                    (i + len(keyword.value) < len(self._code) and is_alphanumeric(self._code[i + len(keyword.value)]))
                ):
                    tokens.append(RawToken(keyword, keyword.value))
                    i += len(keyword.value)
                    kw = True
                    break
            if kw:
                continue

            match c:
                case _ if 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122:
                    tokens.append(RawToken(RawTokenType.TkCharacter, c))
                    i += 1
                    continue
                case _ if 48 <= ord(c) <= 57:
                    tokens.append(RawToken(RawTokenType.TkDigit, c))
                    i += 1
                    continue
                case _:
                    tokens.append(RawToken(RawTokenType.TkUnknown, c))
                    i += 1
                    continue

        # Add a final end-of-file token.
        tokens.append(RawToken(RawTokenType.EndOfFile, ""))
        return tokens


__all__ = ["SppLexer"]
