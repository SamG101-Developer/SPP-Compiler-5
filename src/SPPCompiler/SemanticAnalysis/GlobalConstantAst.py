from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Token import Token


@dataclass
class GlobalConstantAst(Ast):
    annotations: Seq[AnnotationAst]
    tok_cmp: TokenAst
    identifier: IdentifierAst
    tok_colon: Token
    type: TypeAst
    tok_assign: TokenAst
    value: ExpressionAst


__all__ = ["GlobalConstantAst"]
