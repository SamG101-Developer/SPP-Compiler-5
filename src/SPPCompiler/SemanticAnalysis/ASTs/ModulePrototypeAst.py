from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ModuleImplementationAst import ModuleImplementationAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class ModulePrototypeAst(Ast):
    body: ModuleImplementationAst
    tok_eof: TokenAst


__all__ = ["ModulePrototypeAst"]
