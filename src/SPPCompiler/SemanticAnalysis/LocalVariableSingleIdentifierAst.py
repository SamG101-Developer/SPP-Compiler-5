from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class LocalVariableSingleIdentifierAst(Ast):
    tok_mut: Optional[TokenAst]
    name: IdentifierAst


__all__ = ["LocalVariableSingleIdentifierAst"]
