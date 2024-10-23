from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class GenericCompParameterVariadicAst(Ast):
    tok_cmp: TokenAst
    tok_variadic: TokenAst
    name: IdentifierAst
    tok_colon: TokenAst
    type: TypeAst

    def __post_init__(self):
        from SPPCompiler.SemanticAnalysis import TypeAst
        self.name = TypeAst.from_identifier(self.name)


__all__ = ["GenericCompParameterVariadicAst"]