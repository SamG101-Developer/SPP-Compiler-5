from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.FunctionParameterGroupAst import FunctionParameterGroupAst
    from SPPCompiler.SemanticAnalysis.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.InnerScopeAst import InnerScopeAst
    from SPPCompiler.SemanticAnalysis.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.SupPrototypeAst import SupPrototypeAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.WhereBlockAst import WhereBlockAst
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst


@dataclass
class FunctionPrototypeAst(Ast):
    annotations: Seq[AnnotationAst]
    tok_fun: TokenAst
    name: IdentifierAst
    generic_parameter_group: Optional[GenericParameterGroupAst]
    function_parameter_group: FunctionParameterGroupAst
    tok_arrow: TokenAst
    return_type: TypeAst
    where_block: Optional[WhereBlockAst]
    body: InnerScopeAst[StatementAst]

    _orig: IdentifierAst = field(default=None, kw_only=True, repr=False)
    _ctx: ModulePrototypeAst | SupPrototypeAst = field(default=None, kw_only=True, repr=False)
    _abstract: bool = field(default=False, kw_only=True, repr=False)
    _virtual: bool = field(default=False, kw_only=True, repr=False)

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, InnerScopeAst, WhereBlockAst
        self.annotations = Seq(self.annotations)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or InnerScopeAst.default()


__all__ = ["FunctionPrototypeAst"]
