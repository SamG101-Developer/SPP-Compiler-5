from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class LocalVariableSingleIdentifierAst(Ast):
    tok_mut: Optional[TokenAst]
    name: IdentifierAst


__all__ = ["LocalVariableSingleIdentifierAst"]
