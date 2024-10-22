from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.SupMemberAst import SupMemberAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.WhereBlockAst import WhereBlockAst
    from SPPCompiler.SemanticAnalysis.InnerScopeAst import InnerScopeAst


@dataclass
class SupPrototypeFunctionsAst(Ast):
    tok_sup: TokenAst
    generic_parameter_group: GenericParameterGroupAst
    name: TypeAst
    where_block: Optional[WhereBlockAst]
    body: InnerScopeAst[SupMemberAst]

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, InnerScopeAst, WhereBlockAst
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or InnerScopeAst.default()


__all__ = ["SupPrototypeFunctionsAst"]
