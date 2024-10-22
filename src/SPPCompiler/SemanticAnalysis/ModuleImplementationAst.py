from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ModuleMemberAst import ModuleMemberAst


@dataclass
class ModuleImplementationAst(Ast):
    members: Seq[ModuleMemberAst]


__all__ = ["ModuleImplementationAst"]
