from __future__ import annotations
from typing import Callable, Optional, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType
    from SPPCompiler.SyntacticAnalysis.Parser import Parser
    from SPPCompiler.SyntacticAnalysis.ParserAlternateRulesHandler import ParserAlternateRulesHandler


class ParserRuleHandler[T]:
    ParserRule = Callable[[], T]
    __slots__ = ["_rule", "_parser", "_for_alternate", "_result"]

    _rule: ParserRule
    _parser: Parser
    _for_alternate: bool
    _result: Optional[T | Seq[T]]

    def __init__(self, parser: Parser, rule: ParserRule) -> None:
        self._parser = parser
        self._rule = rule
        self._for_alternate = False
        self._result = None

    def parse_once(self, save: bool = True) -> T:
        ast = self._rule()
        if save: self._result = ast
        return ast

    def parse_optional(self, save=True) -> Optional[T]:
        from SPPCompiler.SyntacticAnalysis.ParserError import ParserError

        parser_index = self._parser._index
        try:
            ast = self._rule()
            if save: self._result = ast
            return ast
        except ParserError:
            self._parser._index = parser_index
            return None

    def parse_zero_or_more(self, separator: TokenType, *, propagate_error: bool = False) -> Seq[T]:
        from SPPCompiler.SyntacticAnalysis.ParserError import ParserError

        self._result = Seq()
        i = 0
        parsed_sep = False
        error = None
        while True:
            try:
                if i > 0:
                    self._parser.parse_token(separator).parse_once()
                    parsed_sep = True
                ast = self.parse_once(save=False)
                parsed_sep = False
                self._result.append(ast)
                i += 1
            except ParserError as e:
                if parsed_sep:
                    self._parser._index -= 1
                error = e
                break
        return self._result if not propagate_error else (self._result, error)

    def parse_one_or_more(self, separator: TokenType) -> Seq[T]:
        result = self.parse_zero_or_more(separator, propagate_error=True)
        if result[0].length < 1:
            raise result[1]
        return self._result

    def parse_two_or_more(self, separator: TokenType) -> Seq[T]:
        result = self.parse_zero_or_more(separator, propagate_error=True)
        if result[0].length < 2:
            raise result[1]
        return self._result

    def for_alt(self) -> ParserRuleHandler:
        assert not self._for_alternate
        self._for_alternate = True
        return self

    def __or__(self, that: ParserRuleHandler) -> ParserAlternateRulesHandler:
        from SPPCompiler.SyntacticAnalysis.ParserAlternateRulesHandler import ParserAlternateRulesHandler

        if not (self._for_alternate and that._for_alternate):
            raise SystemExit("Cannot use '|' operator on a non-alternate rule.")

        return ParserAlternateRulesHandler(self._parser).for_alt().add_parser_rule_handler(self).add_parser_rule_handler(that)


__all__ = ["ParserRuleHandler"]
