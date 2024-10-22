from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.UseStatementNamespaceReductionAst import UseStatementNamespaceReductionAst
    from SPPCompiler.SemanticAnalysis.UseStatementTypeAliasAst import UseStatementTypeAliasAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class UseStatementAst(Ast):
    annotations: Seq[AnnotationAst]
    tok_use: TokenAst
    body: UseStatementNamespaceReductionAst | UseStatementTypeAliasAst


__all__ = ["UseStatementAst"]
