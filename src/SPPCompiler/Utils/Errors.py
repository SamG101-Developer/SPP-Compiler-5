from __future__ import annotations
from colorama import Fore, Style
from dataclasses import dataclass
from fastenum import Enum
from ordered_set import OrderedSet
from typing import List, NoReturn, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType
    from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter


class ParserError(Exception):
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


class SemanticError(Exception):
    class Format(Enum):
        NORMAL = 0
        MINIMAL = 1
        NONE = 2

    @dataclass
    class ErrorInfo:
        pos: int
        tag: str
        msg: str
        tip: str
        fmt: SemanticError.Format

    error_info: List[ErrorInfo]

    def __init__(self, *args) -> None:
        super().__init__(args)
        self.error_info = []

    def add_error(self, pos: int, tag: str, msg: str, tip: str, fmt: Format = Format.NORMAL) -> SemanticError:
        # Add an error into the output list.
        self.error_info.append(SemanticError.ErrorInfo(pos, tag, msg, tip, fmt))
        return self

    def add_info(self, pos: int, tag: str) -> SemanticError:
        # Add an info message (minimal error metadata) into the output list.
        self.add_error(pos, tag, "", "", SemanticError.Format.MINIMAL)
        return self

    def _format_message(self, error_info: ErrorInfo) -> (str, bool):
        # For minimal formatting, the message remains empty, as a "tag" is provided.
        if error_info.fmt == SemanticError.Format.MINIMAL:
            return "", True

        # Otherwise, combine the message and tip into a single color-formatted string.
        f = f"\n{Style.BRIGHT}Semantic Error: {Style.NORMAL}{error_info.msg}\n{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Tip: {Style.NORMAL}{error_info.tip}"
        return f, False

    def throw(self, error_formatter: ErrorFormatter) -> NoReturn:
        error_message = ""
        for error in self.error_info:
            formatted_message, is_minimal = self._format_message(error)
            error_message += error_formatter.error(error.pos, formatted_message, error.tag, is_minimal)
        raise SystemError(error_message)


__all__ = ["ParserError"]
