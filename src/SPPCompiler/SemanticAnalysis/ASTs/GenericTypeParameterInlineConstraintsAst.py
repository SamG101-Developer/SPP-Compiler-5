from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class GenericTypeParameterInlineConstraintsAst(Ast):
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    constraints: Seq[Asts.TypeAst] = field(default_factory=Seq)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.constraints:
            string = [
                self.tok_colon.print(printer),
                self.constraints.print(printer, ", ")]
        else:
            string = []
        return "".join(string)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        for c in self.constraints:
            c.analyse_semantics(scope_manager, **kwargs)

        # Check there are duplicate constraints types.
        for i, t in self.constraints.enumerate():
            for j, u in self.constraints[i + 1:].enumerate():
                if t.symbolic_eq(u, scope_manager.current_scope):
                    raise SemanticErrors.IdentifierDuplicationError(t, u).scopes(scope_manager.current_scope)


__all__ = ["GenericTypeParameterInlineConstraintsAst"]
