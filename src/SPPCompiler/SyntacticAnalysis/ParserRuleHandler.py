from __future__ import annotations
from typing import Callable, Optional, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType
    from SPPCompiler.SyntacticAnalysis.Parser import Parser
    from SPPCompiler.SyntacticAnalysis.ParserAlternateRulesHandler import ParserAlternateRulesHandler
    from SPPCompiler.SyntacticAnalysis.ParserError import ParserError


class ParserRuleHandler[T]:
    ParserRule = Callable[[], T]

    _rule: ParserRule
    _parser: Parser
    _for_alternate: bool
    _result: Optional[T | Seq[T]]

    def __init__(self, parser: Parser, rule: ParserRule) -> None:
        self._parser = parser
        self._rule = rule
        self._for_alternate = False
        self._result = None

    def parse_once(self) -> T:
        self._result = self._rule()
        return self._result

    def parse_optional(self, save=True) -> Optional[T]:
        parser_index = self._parser._index
        try:
            ast = self._rule()
            if save: self._result = ast
            return ast
        except ParserError:
            self._parser._index = parser_index
            return None

    def parse_zero_or_more(self, separator: TokenType = TokenType.NO_TOK) -> Seq[T]:
        self._result = Seq()
        i = 0
        while True:
            try:
                if i > 0:
                    self._parser.parse_token(separator).parse_once()
                ast = self.parse_once()
                self._result.append(ast)
                i += 1
            except ParserError:
                break
        return self._result

    def parse_one_or_more(self, separator: TokenType = TokenType.NO_TOK) -> Seq[T]:
        self.parse_zero_or_more(separator)
        if not self._result:
            new_error = ParserError(f"Expected one or more {self._rule}.")
            new_error.pos = self._parser._index
            self._parser._errors.append(new_error)
            raise new_error
        return self._result

    def parse_two_or_more(self, separator: TokenType = TokenType.NO_TOK) -> Seq[T]:
        self.parse_one_or_more(separator)
        if len(self._result) < 2:
            new_error = ParserError(f"Expected two or more {self._rule}.")
            new_error.pos = self._parser._index
            self._parser._errors.append(new_error)
            raise new_error
        return self._result

    def for_alt(self) -> ParserRuleHandler:
        assert not self._for_alternate
        self._for_alternate = True
        return self

    def and_then(self, wrapper_function) -> ParserRuleHandler:
        new_parser_rule_handler = ParserRuleHandler(self._parser, self._rule)
        new_parser_rule_handler._rule = lambda: wrapper_function(self._rule())
        return new_parser_rule_handler

    def __or__(self, that: ParserRuleHandler) -> ParserAlternateRulesHandler:
        from SPPCompiler.SyntacticAnalysis.ParserAlternateRulesHandler import ParserAlternateRulesHandler

        if not (self._for_alternate and that._for_alternate):
            raise SystemExit("Cannot use '|' operator on a non-alternate rule.")

        return ParserAlternateRulesHandler(self._parser).for_alt().add_parser_rule_handler(self).add_parser_rule_handler(that)


__all__ = ["ParserRuleHandler"]
