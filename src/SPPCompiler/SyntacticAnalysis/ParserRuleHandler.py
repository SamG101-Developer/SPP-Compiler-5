from __future__ import annotations
from typing import Callable, Optional, Final, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType
    from SPPCompiler.SyntacticAnalysis.Parser import Parser
    from SPPCompiler.SyntacticAnalysis.ParserAlternateRulesHandler import ParserAlternateRulesHandler


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

    def parse_zero_or_more(self, separator: TokenType, *, propagate_error: bool = False) -> Seq[T]:
        from SPPCompiler.Utils.Errors import ParserError

        result = Seq()
        i = 0
        parsed_sep = False
        error = None
        while True:
            try:
                if i > 0:
                    self._parser.parse_token(separator).parse_once()
                    parsed_sep = True
                ast = self.parse_once()
                parsed_sep = False
                result.append(ast)
                i += 1
            except ParserError as e:
                if parsed_sep:
                    self._parser._index -= 1
                error = e
                break
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
