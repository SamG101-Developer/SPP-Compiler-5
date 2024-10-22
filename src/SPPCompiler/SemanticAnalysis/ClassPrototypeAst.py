from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.WhereBlockAst import WhereBlockAst
    from SPPCompiler.SemanticAnalysis.ClassAttributeAst import ClassAttributeAst
    from SPPCompiler.SemanticAnalysis.InnerScopeAst import InnerScopeAst


@dataclass
class ClassPrototypeAst(Ast):
    annotations: Seq[AnnotationAst]
    tok_cls: TokenAst
    name: TypeAst
    generic_parameter_group: Optional[GenericParameterGroupAst]
    where_block: Optional[WhereBlockAst]
    body: InnerScopeAst[ClassAttributeAst]

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, InnerScopeAst, TypeAst, WhereBlockAst
        self.name = TypeAst.from_identifier(self.name)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or InnerScopeAst.default()


__all__ = ["ClassPrototypeAst"]
