from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.UseStatementNamespaceReductionBodyAst import UseStatementNamespaceReductionBodyAst


@dataclass
class UseStatementNamespaceReductionAst(Ast):
    body: UseStatementNamespaceReductionBodyAst

    _generated: bool = field(default=False, init=False, repr=False)
    _new_asts: Seq[Ast] = field(default_factory=Seq, init=False, repr=False)


__all__ = ["UseStatementNamespaceReductionAst"]
