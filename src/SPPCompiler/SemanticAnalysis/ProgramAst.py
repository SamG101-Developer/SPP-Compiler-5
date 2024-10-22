from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class ProgramAst(Ast):
    module: ModulePrototypeAst
    tok_eof: TokenAst


__all__ = ["ProgramAst"]
