from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstVisbility import visibility_enabled_ast
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
@visibility_enabled_ast
class GlobalConstantAst(Ast, Stage1_PreProcessor):
    annotations: Seq[AnnotationAst]
    tok_cmp: TokenAst
    identifier: IdentifierAst
    tok_colon: TokenAst
    type: TypeAst
    tok_assign: TokenAst
    value: ExpressionAst

    def __post_init__(self) -> None:
        # Convert the annotations into a sequence.
        self.annotations = Seq(self.annotations)

    def pre_process(self, context: PreProcessingContext) -> None:
        self.annotations.for_each(lambda a: a.pre_process(self))


__all__ = ["GlobalConstantAst"]