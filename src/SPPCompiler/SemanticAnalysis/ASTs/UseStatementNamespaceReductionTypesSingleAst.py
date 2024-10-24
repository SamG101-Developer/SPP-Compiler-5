from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementNamespaceReductionTypeAliasAst import UseStatementNamespaceReductionTypeAliasAst


@dataclass
class UseStatementNamespaceReductionTypesSingleAst(Ast):
    namespace: Seq[IdentifierAst]
    types: Seq[GenericIdentifierAst]  # Only 1, loaded into a list for consistency with multiple types.
    alias: Optional[UseStatementNamespaceReductionTypeAliasAst]

    def __post_init__(self) -> None:
        # Convert the namespace and types into a sequence.
        self.namespace = Seq(self.namespace)
        self.types = Seq(self.types)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.namespace.print(printer, "::") + "::" if self.namespace else "",
            self.types.print(printer),
            self.alias.print(printer) if self.alias else ""]
        return "".join(string)


__all__ = ["UseStatementNamespaceReductionTypesSingleAst"]
