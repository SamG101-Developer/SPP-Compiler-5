from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class GenericTypeParameterInlineConstraintsAst(Asts.Ast):
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    constraints: list[Asts.TypeAst] = field(default_factory=list)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.constraints:
            string = [
                self.tok_colon.print(printer),
                SequenceUtils.print(printer, self.constraints, sep=", ")]
        else:
            string = []
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.constraints[-1].pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        for c in self.constraints:
            c.analyse_semantics(sm, **kwargs)

        # Check there are duplicate constraints types.
        for i, t in enumerate(self.constraints):
            for j, u in enumerate(self.constraints[i + 1:]):
                if AstTypeUtils.symbolic_eq(t, u, sm.current_scope, sm.current_scope):
                    raise SemanticErrors.IdentifierDuplicationError().add(
                        t, u, "constraint").scopes(sm.current_scope)


__all__ = [
    "GenericTypeParameterInlineConstraintsAst"]
