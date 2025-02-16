from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class SupImplementationAst(Ast):
    tok_left_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceL))
    members: Seq[Asts.SupMemberAst] = field(default_factory=Seq)
    tok_right_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceR))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.members:
            string = [
                self.tok_left_brace.print(printer) + "\n",
                self.members.print(printer, "\n"),
                self.tok_right_brace.print(printer) + "\n"]
        else:
            string = [
                self.tok_left_brace.print(printer),
                self.tok_right_brace.print(printer) + "\n"]
        return "".join(string)

    def pre_process(self, context: PreProcessingContext) -> None:
        for member in self.members: member.pre_process(context)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.generate_top_level_scopes(scope_manager)

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        for member in self.members: member.generate_top_level_aliases(scope_manager, **kwargs)

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.load_super_scopes(scope_manager)

    def relink_sup_scopes_to_generic_aliases(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.relink_sup_scopes_to_generic_aliases(scope_manager)

    def relink_sup_scopes_to_generic_types(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.relink_sup_scopes_to_generic_types(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        for member in self.members: member.analyse_semantics(scope_manager, **kwargs)


__all__ = ["SupImplementationAst"]
