from __future__ import annotations
from typing import Callable, Final, Optional, Tuple, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType
    from SPPCompiler.SyntacticAnalysis.Parser import Parser
    from SPPCompiler.SyntacticAnalysis.ParserAlternateRulesHandler import ParserAlternateRulesHandler
    from SPPCompiler.Utils.Errors import ParserError


class ParserRuleHandler[T]:
    ParserRule = Callable[[], T]
    __slots__ = ["_rule", "_parser"]

    _rule: Final[ParserRule]
    _parser: Final[Parser]

    def __init__(self, parser: Parser, rule: ParserRule) -> None:
        self._parser = parser
        self._rule = rule

    def parse_once(self) -> T:
        ast = self._rule()
        return ast

    def parse_optional(self) -> Optional[T]:
        from SPPCompiler.Utils.Errors import ParserError

        parser_index = self._parser._index
        try:
            ast = self._rule()
            return ast
        except ParserError:
            self._parser._index = parser_index
            return None

    def parse_zero_or_more(self, separator: TokenType, *, propagate_error: bool = False) -> Seq[T] | Tuple[Seq[T], ParserError]:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.Utils.Errors import ParserError

        successful_parses, result = 0, Seq()
        parsed_sep, error = False, None
        while True:
            try:
                # If this is the second pass, then require the separator to be parsed.
                if successful_parses > 0:
                    self._parser.parse_token(separator).parse_once()
                    parsed_sep = True

                # Try to parse the AST, and mark the most recent parse as non-separator.
                ast = self.parse_once()
                parsed_sep = False

                # Save the AST to the result list and increment the number of ASTs parsed.
                result.append(ast)
                successful_parses += 1

            except ParserError as e:
                # If the most recent parse is a separator, backtrack it because there is no following AST.
                if parsed_sep:
                    self._parser._index -= 1 * (separator != TokenType.NO_TOK)

                # Save the error and break the loop.
                error = e
                break

        # Return the result, and the with the error if it is to be propagated.
        return result if not propagate_error else (result, error)

    def parse_one_or_more(self, separator: TokenType) -> Seq[T]:
        result = self.parse_zero_or_more(separator, propagate_error=True)
        if result[0].length < 1:
            raise result[1]
        return result[0]

    def parse_two_or_more(self, separator: TokenType) -> Seq[T]:
        result = self.parse_zero_or_more(separator, propagate_error=True)
        if result[0].length < 2:
            raise result[1]
        return result[0]

    def __or__(self, that: ParserRuleHandler) -> ParserAlternateRulesHandler:
        from SPPCompiler.SyntacticAnalysis.ParserAlternateRulesHandler import ParserAlternateRulesHandler
        return ParserAlternateRulesHandler(self._parser).add_parser_rule_handler(self).add_parser_rule_handler(that)


__all__ = ["ParserRuleHandler"]
