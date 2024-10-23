from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ModuleMemberAst import ModuleMemberAst


@dataclass
class ModuleImplementationAst(Ast):
    members: Seq[ModuleMemberAst]

    def __post_init__(self) -> None:
        self.members = Seq(self.members)


__all__ = ["ModuleImplementationAst"]