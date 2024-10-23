from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.NumberLiteralAst import NumberLiteralAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class ArrayLiteral0ElementAst(Ast):
    tok_left_bracket: TokenAst
    type: TypeAst
    tok_comma: TokenAst
    size: NumberLiteralAst
    tok_right_bracket: TokenAst


__all__ = ["ArrayLiteral0ElementAst"]
