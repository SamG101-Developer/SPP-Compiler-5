from __future__ import annotations

from collections import OrderedDict
from typing import Any, List, Tuple
from fastenum.fastenum import Enum, EnumMeta
import re


class TokenTypeMeta(EnumMeta):
    # When created, create compiled regexes for lexemes

    def __new__(mcs, cls: str, bases: Tuple[type], classdict: OrderedDict[str, Any]) -> TokenTypeMeta:
        new_members = type(classdict)()
        for key, value in classdict.items():
            if key.startswith("Lx"):
                new_members[f"Cm{key}"] = re.compile(value)
        new_members.update(classdict)
        return super(TokenTypeMeta, mcs).__new__(mcs, cls, bases, new_members)


class TokenType(Enum, metaclass=TokenTypeMeta):
    # Comparison operations
    TkEq = "=="
    TkNe = "!="
    TkLe = "<="
    TkGe = ">="
    TkLt = "<"
    TkGt = ">"
    TkSs = "<=>"

    # Arithmetic operations
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

    # Brackets
    TkParenL = "("
    TkParenR = ")"
    TkBrackL = "["
    TkBrackR = "]"
    TkBraceL = "{"
    TkBraceR = "}"

    # Other symbols
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

    TkEOF = "<EOF>"
    TkWhitespace = " "
    TkNewLine = "\n"
    TkDollar = "$"

    # Keywords
    # Module level declarations
    KwCls = "cls"
    KwSup = "sup"
    KwFun = "fun"
    KwCor = "cor"
    KwUse = "use"
    KwExt = "ext"

    # Variable declarations
    KwCmp = "cmp"
    KwLet = "let"
    KwMut = "mut"
    KwPin = "pin"
    KwRel = "rel"

    # Control flow
    KwCase = "case"
    KwElse = "else"
    KwLoop = "loop"
    KwWith = "with"
    KwSkip = "skip"
    KwExit = "exit"
    KwStep = "step"

    # Control flow exit
    KwRet = "ret"
    KwGen = "gen"

    # Type helpers
    KwWhere = "where"
    KwAs = "as"
    KwIsNot = "is not"
    KwIs = "is"

    # Types
    KwTrue = "true"
    KwFalse = "false"
    KwSelf = "self"
    KwSelfType = "Self"

    # Logical operators
    KwAnd = "and"
    KwOr = "or"
    KwNot = "not"

    # Misc
    KwOf = "of"
    KwIn = "in"
    KwAsync = "async"

    # Lexemes
    LxIdentifier = r"\$?[a-z][_a-z0-9]*"
    LxUpperIdentifier = r"\$?[A-Z][_a-zA-Z0-9]*"
    LxBinDigits = r"0b[01]+"
    LxHexDigits = r"0x[0-9a-fA-F]+"
    LxDecInteger = r"[0-9]([0-9_]*[0-9])?"
    LxDoubleQuoteStr = r"\"[^\"]*\""
    LxMultiLineComment = r"##[^#]*##"
    LxSingleLineComment = r"#.*"

    # Unknown token to shift error to ErrFmt
    ERR = "Unknown"
    NO_TOK = ""

    def print(self) -> str:
        return f"<{self.name[2:]}>" if self.name[:2] == "Cm" else self.value

    def __json__(self) -> str:
        return self.value


class TokenTypeSet:
    TOKENS = sorted([tok for tok in TokenType if tok.name.startswith("Tk")], key=lambda t: len(t.value), reverse=True)
    KEYWORDS = sorted([tok for tok in TokenType if tok.name.startswith("Kw")], key=lambda t: len(t.value), reverse=True)
    LEXEMES = [tok for tok in TokenType if tok.name.startswith("Lx")]
    COMPILED_LEXEMES = [tok for tok in TokenType if tok.name.startswith("Cm")]
    ALL = KEYWORDS + COMPILED_LEXEMES + TOKENS


__all__ = ["TokenType"]
