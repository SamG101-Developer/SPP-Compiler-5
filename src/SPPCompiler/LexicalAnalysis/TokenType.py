from __future__ import annotations
from dataclasses import dataclass
from fastenum import Enum
import json_fix


class TokenType(Enum):
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
    Pin = "pin"
    Rel = "rel"
    Is = "is"
    As = "as"
    Or = "or"
    And = "and"
    Not = "not"
    Async = "async"
    Step = "step"
    True_ = "true"
    False_ = "false"


class SppTokenType(TokenType):
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
    KwPin = "pin"
    KwRel = "rel"
    KwCase = "case"
    KwElse = "else"
    KwLoop = "loop"
    KwWith = "with"
    KwSkip = "skip"
    KwExit = "exit"
    KwStep = "step"
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

    TkEq = "=="
    TkNe = "!="
    TkLe = "<="
    TkGe = ">="
    TkLt = "<"
    TkGt = ">"
    TkSs = "<=>"
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
    def whitespace_token() -> SppTokenType:
        return SppTokenType.TkWhitespace

    @staticmethod
    def newline_token() -> SppTokenType:
        return SppTokenType.TkNewLine


@dataclass
class RawToken:
    token_type: RawTokenType
    token_data: str


__all__ = ["SppTokenType"]
