from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.UseStatementNamespaceReductionBodyAst import UseStatementNamespaceReductionBodyAst


@dataclass
class UseStatementNamespaceReductionTypesMultipleAst(Ast):
    namespace: Seq[IdentifierAst]
    tok_left_brace: TokenAst
    types: Seq[UseStatementNamespaceReductionBodyAst]
    tok_right_brace: TokenAst


__all__ = ["UseStatementNamespaceReductionTypesMultipleAst"]
