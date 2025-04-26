from __future__ import annotations

from dataclasses import dataclass

from enum import Enum


class TokenType(Enum):
    """!
    The base class for all token types. Provides uniform access to newline and whitespace tokens.
    """

    @staticmethod
    def newline_token() -> TokenType:
        ...

    @staticmethod
    def whitespace_token() -> TokenType:
        ...

    def print(self) -> str:
        return self.value

    def __json__(self) -> str:
        return self.value


class RawTokenType(TokenType):
    """!
    The RawTokenType class is a set of tokens that the lexer can recognize. These tokens are single-length, and will be
    combined in the parser to make more advanced tokens.
    """

    TkCharacter = 0
    TkDigit = 1
    TkEqualsSign = 2
    TkPlusSign = 3
    TkMinusSign = 4
    TkAsterisk = 5
    TkForwardSlash = 6
    TkPercentSign = 7
    TkCaret = 8
    TkLessThanSign = 9
    TkGreaterThanSign = 10
    TkLeftParenthesis = 11
    TkRightParenthesis = 12
    TkLeftSquareBracket = 13
    TkRightSquareBracket = 14
    TkLeftCurlyBrace = 15
    TkRightCurlyBrace = 16
    TkQuestionMark = 17
    TkColon = 18
    TkAmpersand = 19
    TkDot = 21
    TkComma = 22
    TkAt = 23
    TkUnderscore = 24
    TkSpeechMark = 25
    TkWhitespace = 26
    TkNewLine = 27
    TkDollar = 28
    TkUnknown = 29
    NoToken = 30
    Keyword = 31
    EndOfFile = 32
    TkExclamationMark = 33

    @staticmethod
    def newline_token() -> TokenType:
        return RawTokenType.TkNewLine

    @staticmethod
    def whitespace_token() -> TokenType:
        return RawTokenType.TkWhitespace


class RawKeywordType(TokenType):
    """!
    The RawKeywordType class is a set of keywords that are used for the parser to know, for a specific keyword, which
    characters to parse. The final TokenAst will not contain a RawKeywordType, but the matching SppTokenType.
    """

    Cls = "cls"
    Fun = "fun"
    Cor = "cor"
    Sup = "sup"
    Ext = "ext"
    Mut = "mut"
    Use = "use"
    Cmp = "cmp"
    Let = "let"
    Where = "where"
    SelfVal = "self"
    SelfType = "Self"
    Case = "case"
    Of = "of"
    Loop = "loop"
    In = "in"
    Else = "else"
    Gen = "gen"
    With = "with"
    Ret = "ret"
    Exit = "exit"
    Skip = "skip"
    Is = "is"
    As = "as"
    Or = "or"
    And = "and"
    Not = "not"
    Async = "async"
    True_ = "true"
    False_ = "false"
    Res = "res"


class SppTokenType(TokenType):
    """!
    The SppTokenType class contains all the keyword and tokens that are created by the parser, and stored inside
    TokenAsts.
    """

    LxNumber = "<char>"
    LxString = "<num>"

    KwCls = "cls"
    KwSup = "sup"
    KwFun = "fun"
    KwCor = "cor"
    KwUse = "use"
    KwExt = "ext"
    KwCmp = "cmp"
    KwLet = "let"
    KwMut = "mut"
    KwCase = "case"
    KwElse = "else"
    KwLoop = "loop"
    KwWith = "with"
    KwSkip = "skip"
    KwExit = "exit"
    KwRet = "ret"
    KwGen = "gen"
    KwWhere = "where"
    KwAs = "as"
    KwIsNot = "is not"
    KwIs = "is"
    KwTrue = "true"
    KwFalse = "false"
    KwSelfVal = "self"
    KwSelfType = "Self"
    KwAnd = "and"
    KwOr = "or"
    KwNot = "not"
    KwOf = "of"
    KwIn = "in"
    KwAsync = "async"
    KwRes = "res"

    TkEq = "=="
    TkNe = "!="
    TkLe = "<="
    TkGe = ">="
    TkLt = "<"
    TkGt = ">"
    TkPlus = "+"
    TkMinus = "-"
    TkMultiply = "*"
    TkDivide = "/"
    TkRemainder = "%"
    TkModulo = "%%"
    TkExponent = "**"
    TkPlusAssign = "+="
    TkMinusAssign = "-="
    TkMultiplyAssign = "*="
    TkDivideAssign = "/="
    TkRemainderAssign = "%="
    TkModuloAssign = "%%="
    TkExponentAssign = "**="
    TkLeftParenthesis = "("
    TkRightParenthesis = ")"
    TkLeftSquareBracket = "["
    TkRightSquareBracket = "]"
    TkLeftCurlyBrace = "{"
    TkRightCurlyBrace = "}"
    TkQuestionMark = "?"
    TkDoubleDot = ".."
    TkColon = ":"
    TkAmpersand = "&"
    TkDot = "."
    TkDoubleColon = "::"
    TkComma = ","
    TkAssign = "="
    TkArrowR = "->"
    TkAt = "@"
    TkSpeechMark = "\""
    TkUnderscore = "_"
    TkWhitespace = " "
    TkNewLine = "\n"
    TkDollar = "$"

    NoToken = ""

    @staticmethod
    def newline_token() -> SppTokenType:
        return SppTokenType.TkNewLine

    @staticmethod
    def whitespace_token() -> SppTokenType:
        return SppTokenType.TkWhitespace


@dataclass(slots=True)
class RawToken:
    """!
    A RawToken allows for pairing metadata will a RawTokenType. For example, when "a" is lexed, the RawToken will
    contain a RawTokenType.TkCharacter with the data "a".
    """

    token_type: RawTokenType
    token_data: str


__all__ = [
    "RawTokenType",
    "RawKeywordType",
    "RawToken",
    "SppTokenType"]
