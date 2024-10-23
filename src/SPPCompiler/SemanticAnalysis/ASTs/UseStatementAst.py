from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstVisbility import visibility_enabled_ast
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementNamespaceReductionAst import UseStatementNamespaceReductionAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementTypeAliasAst import UseStatementTypeAliasAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
@visibility_enabled_ast
class UseStatementAst(Ast, Stage1_PreProcessor):
    annotations: Seq[AnnotationAst]
    tok_use: TokenAst
    body: UseStatementNamespaceReductionAst | UseStatementTypeAliasAst

    def __post_init__(self) -> None:
        self.annotations = Seq(self.annotations)

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the annotations of this use statement.
        Seq(self.annotations).for_each(lambda a: a.pre_process(self))


__all__ = ["UseStatementAst"]
