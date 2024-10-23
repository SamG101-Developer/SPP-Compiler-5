from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstVisbility import visibility_enabled_ast
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.ClassAttributeAst import ClassAttributeAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereBlockAst import WhereBlockAst


@dataclass
@visibility_enabled_ast
class ClassPrototypeAst(Ast, Stage1_PreProcessor):
    annotations: Seq[AnnotationAst]
    tok_cls: TokenAst
    name: TypeAst
    generic_parameter_group: GenericParameterGroupAst
    where_block: WhereBlockAst
    body: InnerScopeAst[ClassAttributeAst]

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, InnerScopeAst
        from SPPCompiler.SemanticAnalysis import TypeAst, WhereBlockAst

        # Convert the annotations into a sequence, the name to a TypeAst, and other defaults.
        self.annotations = Seq(self.annotations)
        self.name = TypeAst.from_identifier(self.name)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or InnerScopeAst.default()

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the annotations and attributes of this class.
        self.annotations.for_each(lambda a: a.pre_process(self))
        self.body.members.for_each(lambda m: m.pre_process(self))


__all__ = ["ClassPrototypeAst"]
