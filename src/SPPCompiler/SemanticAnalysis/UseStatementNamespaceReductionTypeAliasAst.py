from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class UseStatementNamespaceReductionTypeAliasAst(Ast):
    tok_as: TokenAst
    type: TypeAst

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
        self.type = TypeAst.from_identifier(self.type)
