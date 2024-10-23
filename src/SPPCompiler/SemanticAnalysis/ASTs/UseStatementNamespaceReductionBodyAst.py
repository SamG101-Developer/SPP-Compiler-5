from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementNamespaceReductionTypesAst import UseStatementNamespaceReductionTypesAst


@dataclass
class UseStatementNamespaceReductionBodyAst(Ast):
    type: UseStatementNamespaceReductionTypesAst


__all__ = ["UseStatementNamespaceReductionBodyAst"]
