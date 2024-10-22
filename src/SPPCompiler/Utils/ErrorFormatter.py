from typing import List
from colorama import Fore, Style

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.LexicalAnalysis.TokenType import TokenType


class ErrorFormatter:
    _tokens: List[Token]
    _file_path: str

    def __init__(self, tokens: List[Token], file_path: str) -> None:
        self._tokens = tokens
        self._file_path = file_path[file_path.rfind("src\\") + 4:]

    def error(self, start_pos: int, end_pos: int = -1, message: str = "", tag_message: str = "", minimal: bool = False, no_format: bool = False) -> str:
        if no_format:
            return message
        while self._tokens[start_pos].token_type in [TokenType.TkNewLine, TokenType.TkWhitespace]:
            start_pos += 1

        # Get the tokens at the start and end of the line containing the error. Skip the leading newline.
        error_line_start_pos = [i for i, x in enumerate(self._tokens[:start_pos]) if x.token_type == TokenType.TkNewLine][-1] + 1
        error_line_end_pos = ([i for i, x in enumerate(self._tokens[start_pos:]) if x.token_type == TokenType.TkNewLine] or [len(self._tokens) - 1])[0] + start_pos
        error_line_tokens = self._tokens[error_line_start_pos:error_line_end_pos]
        error_line_as_string = "".join([str(token) for token in error_line_tokens])

        # Get the line number of the error
        error_line_number = len([x for x in self._tokens[:start_pos] if x.token_type == TokenType.TkNewLine])

        # The number of "^" is the length of the token data where the error is. Todo: Should span entire AST node.
        if end_pos == -1:
            carets = "^" * len(self._tokens[start_pos].token_metadata)
        else:
            carets = "^" * (end_pos - start_pos)
        carets_line_as_string = f"{carets}"
        carets_line_as_string = " " * sum([len(str(token)) for token in self._tokens[error_line_start_pos : start_pos]]) + carets_line_as_string

        # Print the preceding spaces before the error line
        l1 = len(error_line_as_string)
        error_line_as_string = error_line_as_string.replace("  ", "")
        carets_line_as_string = carets_line_as_string[l1 - len(error_line_as_string):] + f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT} <- {tag_message}"

        left_padding = " " * len(str(error_line_number))
        final_error_message = "\n".join([
            f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}",
            f"Error in file '{self._file_path}', on line {error_line_number}:" if not minimal else f"Context from file '{self._file_path}', on line {error_line_number}:",
            f"{Fore.LIGHTWHITE_EX}{left_padding} |",
            f"{Fore.LIGHTRED_EX if not minimal else Fore.LIGHTGREEN_EX}{error_line_number} | {error_line_as_string}",
            f"{Fore.LIGHTWHITE_EX}{left_padding} | {Style.NORMAL}{Fore.LIGHTRED_EX if not minimal else Fore.LIGHTGREEN_EX}{carets_line_as_string}\n",
            f"{Style.RESET_ALL}{Fore.LIGHTRED_EX}{message}" * (not minimal)])

        return final_error_message
