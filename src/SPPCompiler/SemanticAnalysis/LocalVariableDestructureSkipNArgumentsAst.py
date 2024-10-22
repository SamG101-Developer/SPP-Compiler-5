from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.LocalVariableSingleIdentifierAst import LocalVariableSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class LocalVariableDestructureSkipNArgumentsAst(Ast):
    variadic_token: TokenAst
    binding: Optional[LocalVariableSingleIdentifierAst]
    _num_skipped: int = field(default=0, init=False, repr=False)


__all__ = ["LocalVariableDestructureSkipNArgumentsAst"]
