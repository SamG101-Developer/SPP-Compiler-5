from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class WhereBlockAst(Ast):
    tok_where: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwWhere))
    constraint_group: Asts.WhereConstraintsGroupAst = field(default_factory=lambda: Asts.WhereConstraintsGroupAst())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.constraint_group.constraints:
            string = [
                self.tok_where.print(printer) + " ",
                self.constraint_group.print(printer)]
        else:
            string = []
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.constraint_group.pos_end

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["WhereBlockAst"]
