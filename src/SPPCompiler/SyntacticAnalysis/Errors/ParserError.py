from __future__ import annotations
from abc import ABC
from ordered_set import OrderedSet
from typing import List, NoReturn

from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter


class ParserError(ABC, Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)

    def throw(self, error_formatter: ErrorFormatter) -> NoReturn:
        ...


class ParserErrors:

    class SyntaxError(ParserError):
        pos: int
        expected_tokens: List[TokenType]

        def __init__(self, *args) -> None:
            super().__init__(*args)
            self.pos = -1
            self.expected_tokens = []

        def throw(self, error_formatter: ErrorFormatter) -> NoReturn:
            # Convert the list of expected tokens into a set of strings.
            all_expected_tokens = OrderedSet([t.print() for t in self.expected_tokens])
            all_expected_tokens = "{'" + "' | '".join(all_expected_tokens).replace("\n", "\\n") + "'}"

            # Replace the "$" token with the set of expected tokens.
            error_message = str(self).replace("$", all_expected_tokens)
            error_message = error_formatter.error(self.pos, message=error_message, tag_message="Syntax Error")

            # Raise the error.
            raise ParserError(error_message) from None
