from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class UseStatementTypeAliasAst(Ast):
    new_type: TypeAst
    generic_parameter_group: GenericParameterGroupAst
    tok_assign: TokenAst
    old_type: TypeAst

    _generated: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, TypeAst
        self.new_type = TypeAst.from_identifier(self.new_type)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()


__all__ = ["UseStatementTypeAliasAst"]
