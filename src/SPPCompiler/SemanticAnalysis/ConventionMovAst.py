from __future__ import annotations
from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default


@dataclass
class ConventionMovAst(Ast, Default):

    @staticmethod
    def default() -> Default:
        return ConventionMovAst(-1)


__all__ = ["ConventionMovAst"]
