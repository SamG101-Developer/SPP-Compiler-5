from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.UseStatementNamespaceReductionTypeAliasAst import UseStatementNamespaceReductionTypeAliasAst


@dataclass
class UseStatementNamespaceReductionTypesSingleAst(Ast):
    namespace: Seq[IdentifierAst]
    types: Seq[GenericIdentifierAst]  # Only 1, loaded into a list for consistency with multiple types.
    alias: Optional[UseStatementNamespaceReductionTypeAliasAst]

    def __post_init__(self) -> None:
        self.namespace = Seq(self.namespace)
        self.types = Seq(self.types)


__all__ = ["UseStatementNamespaceReductionTypesSingleAst"]
