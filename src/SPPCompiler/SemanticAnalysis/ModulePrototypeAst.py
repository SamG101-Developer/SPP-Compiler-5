from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ModuleImplementationAst import ModuleImplementationAst


@dataclass
class ModulePrototypeAst(Ast):
    body: ModuleImplementationAst


__all__ = ["ModulePrototypeAst"]
