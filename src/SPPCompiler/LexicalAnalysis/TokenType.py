from __future__ import annotations

from dataclasses import dataclass

from fastenum import Enum


class TokenType(Enum):
    """
    The base class for all token types. Provides uniform access to newline and whitespace tokens.
    """

    @staticmethod
    def newline_token() -> TokenType:
        """
        Gets the token being used by this token set to indicate a "newline".
        :return: The newline token.
        """

    @staticmethod
    def whitespace_token() -> TokenType:
        """
        Gets the token being used by this token set to indicate a "whitespace".
        :return: The whitespace token.
        """

    def print(self) -> str:
        """
        To print a token, return the value of it. This is the string that parses into the token being printed.
        :return: The string representation of the token.
        """

        # Get the value of the token.
        return self.value

    def __json__(self) -> str:
        """
        To get the JSON representation of this token, return the value of it. This is the same as printing the token,
        but inside a JSON context. Allows for tokens to be compatible with recursive ``__json__`` calls from other
        objects.
        :return: The string representation of the token.
        """

        # Get the value of the token.
        return self.value


class RawTokenType(TokenType):
    """
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
    TkVerticalBar = 20
    TkDot = 21
    TkComma = 22
    TkAt = 23
    TkUnderscore = 24
    TkSpeechMark = 25
    TkExclamationMark = 26
    TkWhitespace = 27
    TkNewLine = 28
    TkDollar = 29
    TkUnknown = 30
    NoToken = 31
    EndOfFile = 32

    @staticmethod
    def newline_token() -> TokenType:
        return RawTokenType.TkNewLine

    @staticmethod
    def whitespace_token() -> TokenType:
        return RawTokenType.TkWhitespace


class RawKeywordType(TokenType):
    """
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
    Type = "type"
    Where = "where"
    SelfVal = "self"
    SelfType = "Self"
    Case = "case"
    Iter = "iter"
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
    Caps = "caps"


class SppTokenType(TokenType):
    """
    The SppTokenType class contains all the keyword and tokens that are created by the parser, and stored inside
    TokenAsts.
    """

    LxNumber = "<char>"
    LxString = "<num>"

    KwCls = "cls"
    KwFun = "fun"
    KwCor = "cor"
    KwSup = "sup"
    KwExt = "ext"
    KwMut = "mut"
    KwUse = "use"
    KwCmp = "cmp"
    KwLet = "let"
    KwType = "type"
    KwCase = "case"
    KwElse = "else"
    KwLoop = "loop"
    KwIter = "iter"
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
    KwCaps = "caps"

    TkEq = "=="
    """The token for equality. This is a double equals sign, and is used to compare two values."""

    TkNe = "!="
    """The token for inequality. This is a double exclamation mark, and is used to compare two values."""

    TkLe = "<="
    """The token for less than or equal to. This is a double less than sign, and is used to compare two values."""

    TkGe = ">="
    """The token for greater than or equal to. This is a double greater than sign, and is used to compare two values."""

    TkLt = "<"
    """The token for less than. This is a single less than sign, and is used to compare two values."""

    TkGt = ">"
    """The token for greater than. This is a single greater than sign, and is used to compare two values."""

    TkPlus = "+"
    """The token for addition. This is a single plus sign, and is used to add two values together."""

    TkMinus = "-"
    """The token for subtraction. This is a single minus sign, and is used to subtract two values."""

    TkMultiply = "*"
    """The token for multiplication. This is a single asterisk, and is used to multiply two values together."""

    TkDivide = "/"
    """The token for division. This is a single forward slash, and is used to divide two values."""

    TkRemainder = "%"
    """The token for remainder. This is a single percent sign, and is used to get the remainder of two values."""

    TkExponent = "**"
    """The token for exponentiation. This is a double asterisk, and is used to raise a value to the power of another value."""

    TkPlusAssign = "+="
    """The token for addition assignment. This is a plus sign followed by an equals sign, and is used to add a value to a variable."""

    TkMinusAssign = "-="
    """The token for subtraction assignment. This is a minus sign followed by an equals sign, and is used to subtract a value from a variable."""

    TkMultiplyAssign = "*="
    """The token for multiplication assignment. This is an asterisk followed by an equals sign, and is used to multiply a variable by a value."""

    TkDivideAssign = "/="
    """The token for division assignment. This is a forward slash followed by an equals sign, and is used to divide a variable by a value."""

    TkRemainderAssign = "%="
    """The token for remainder assignment. This is a percent sign followed by an equals sign, and is used to get the remainder of a variable and a value."""

    TkExponentAssign = "**="
    """The token for exponentiation assignment. This is a double asterisk followed by an equals sign, and is used to raise a variable to the power of a value."""

    TkLeftParenthesis = "("
    """The token for a left parenthesis. This is a single left parenthesis, and is used to group expressions together."""

    TkRightParenthesis = ")"
    """The token for a right parenthesis. This is a single right parenthesis, and is used to group expressions together."""

    TkLeftSquareBracket = "["
    """The token for a left square bracket. This is a single left square bracket, and is used to group expressions together."""

    TkRightSquareBracket = "]"
    """The token for a right square bracket. This is a single right square bracket, and is used to group expressions together."""

    TkLeftCurlyBrace = "{"
    """The token for a left curly brace. This is a single left curly brace, and is used to define a scope boundary."""

    TkRightCurlyBrace = "}"
    """The token for a right curly brace. This is a single right curly brace, and is used to define a scope boundary."""

    TkQuestionMark = "?"
    """The token for a question mark. This is a single question mark, and is used for optional types or early returning."""

    TkDoubleDot = ".."
    """The token for a double dot. This is a double dot, and is used for a range tuple operations or defaulting."""

    TkColon = ":"
    """The token for a colon. This is a single colon, and is used for type annotations or constraints."""

    TkAmpersand = "&"
    """The token for an ampersand. This is a single ampersand, and is used to mark borrows."""

    TkVerticalBar = "|"
    """The token for a vertical bar. This is a single vertical bar, and is used to mark a lambda expression."""

    TkLeftShift = "<<"
    """The token for a left shift. This is a double less than sign, and is used to shift bits to the left."""

    TkRightShift = ">>"
    """The token for a right shift. This is a double greater than sign, and is used to shift bits to the right."""

    TkLeftShiftAssign = "<<="
    """The token for a left shift assignment. This is a double less than sign followed by an equals sign, and is used to shift bits to the left and assign the result to a variable."""

    TkRightShiftAssign = ">>="
    """The token for a right shift assignment. This is a double greater than sign followed by an equals sign, and is used to shift bits to the right and assign the result to a variable."""

    TkBitAnd = "&"
    """The token for a bitwise AND. This is a single ampersand, and is used to perform a bitwise AND operation."""

    TkBitIor = "|"
    """The token for a bitwise OR. This is a single vertical bar, and is used to perform a bitwise OR operation."""

    TkBitXor = "^"
    """The token for a bitwise XOR. This is a single caret, and is used to perform a bitwise XOR operation."""

    TkBitAndAssign = "&="
    """The token for a bitwise AND assignment. This is a single ampersand followed by an equals sign, and is used to perform a bitwise AND operation and assign the result to a variable."""

    TkBitIorAssign = "|="
    """The token for a bitwise OR assignment. This is a single vertical bar followed by an equals sign, and is used to perform a bitwise OR operation and assign the result to a variable."""

    TkBitXorAssign = "^="
    """The token for a bitwise XOR assignment. This is a single caret followed by an equals sign, and is used to perform a bitwise XOR operation and assign the result to a variable."""

    TkDot = "."
    """The token for a dot. This is a single dot, and is used to access members of a class or module."""

    TkDoubleColon = "::"
    """The token for a double colon. This is a double colon, and is used for static access to members of a class or module."""

    TkComma = ","
    """The token for a comma. This is a single comma, and is used to separate arguments in a function call or definition."""

    TkAssign = "="
    """The token for an assignment. This is a single equals sign, and is used to assign a value to a variable."""

    TkArrowR = "->"
    """The token for a right arrow. This is a dash followed by a greater than sign, and is used to indicate a function return type."""

    TkAt = "@"
    """The token for an at sign. This is a single at sign, and is used to mark annotations."""

    TkSpeechMark = "\""
    """The token for a speech mark. This is a single double-speech mark, and is used to define a string literal."""

    TkUnderscore = "_"
    """The token for an underscore. This is a single underscore, and is used to indicate a wildcard or ignore a single value."""

    TkExclamationMark = "!"
    """The token for an exclamation mark. This is a single exclamation mark, and is used to bind a generator exception."""

    TkDoubleExclamationMark = "!!"
    """The token for a double exclamation mark. This is used to indicate an exhausted generator."""

    TkWhitespace = " "
    """The token for whitespace. This is a single space, and is used to separate tokens."""

    TkNewLine = "\n"
    """The token for a new line. This is a single new line, and is used to separate lines of code."""

    TkDollar = "$"
    """The token for a dollar sign. This is a single dollar sign, and is used to generate internal types and identifiers."""

    NoToken = ""
    """The token for no token. This is an empty string, and is used to indicate that there is no token (skip)."""

    @staticmethod
    def newline_token() -> SppTokenType:
        return SppTokenType.TkNewLine

    @staticmethod
    def whitespace_token() -> SppTokenType:
        return SppTokenType.TkWhitespace


@dataclass(slots=True, repr=False)
class RawToken:
    """
    A RawToken allows for pairing metadata will a RawTokenType. For example, when "a" is lexed, the RawToken will
    contain a RawTokenType.TkCharacter with the data "a".
    """

    token_type: RawTokenType | RawKeywordType
    token_data: str


__all__ = [
    "RawTokenType",
    "RawKeywordType",
    "RawToken",
    "SppTokenType"]
