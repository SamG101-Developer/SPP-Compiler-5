from __future__ import annotations

from SParLex.Lexer.Tokens import TokenType


class SppTokenType(TokenType):
    LxIdentifier = r"\$?[a-z][_a-z0-9]*"
    LxUpperIdentifier = r"\$?[A-Z][_a-zA-Z0-9]*"
    LxBinDigits = r"0b[01]+"
    LxHexDigits = r"0x[0-9a-fA-F]+"
    LxDecInteger = r"[0-9]([0-9_]*[0-9])?"
    LxDoubleQuoteStr = r"\"[^\"]*\""
    LxMultiLineComment = r"##[^#]*##"
    LxSingleLineComment = r"#.*"

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
    KwSelf = "self"
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
    TkAdd = "+"
    TkSub = "-"
    TkMul = "*"
    TkDiv = "/"
    TkRem = "%"
    TkMod = "%%"
    TkExp = "**"
    TkAddAssign = "+="
    TkSubAssign = "-="
    TkMulAssign = "*="
    TkDivAssign = "/="
    TkRemAssign = "%="
    TkModAssign = "%%="
    TkExpAssign = "**="
    TkParenL = "("
    TkParenR = ")"
    TkBrackL = "["
    TkBrackR = "]"
    TkBraceL = "{"
    TkBraceR = "}"
    TkQst = "?"
    TkVariadic = ".."
    TkColon = ":"
    TkBorrow = "&"
    TkUnion = "|"
    TkDot = "."
    TkDblColon = "::"
    TkComma = ","
    TkAssign = "="
    TkArrowR = "->"
    TkAt = "@"
    TkUnderscore = "_"
    TkWhitespace = " "
    TkNewLine = "\n"
    TkDollar = "$"

    @staticmethod
    def single_line_comment_token() -> SppTokenType:
        return SppTokenType.LxSingleLineComment

    @staticmethod
    def multi_line_comment_token() -> SppTokenType:
        return SppTokenType.LxMultiLineComment

    @staticmethod
    def whitespace_token() -> SppTokenType:
        return SppTokenType.TkWhitespace

    @staticmethod
    def newline_token() -> SppTokenType:
        return SppTokenType.TkNewLine

    def print(self) -> str:
        return self.value

    def __json__(self) -> str:
        return self.value


__all__ = ["SppTokenType"]
