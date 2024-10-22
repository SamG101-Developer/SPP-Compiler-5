from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class FunctionParameterSelfAst(Ast):
    tok_mut: Optional[TokenAst]
    convention: ConventionAst
    name: IdentifierAst
    type: TypeAst = field(default=None, init=False)

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        self.type = CommonTypes.Self(self.pos)

    def __eq__(self, other: FunctionParameterSelfAst) -> bool:
        return isinstance(other, FunctionParameterSelfAst)


__all__ = ["FunctionParameterSelfAst"]
