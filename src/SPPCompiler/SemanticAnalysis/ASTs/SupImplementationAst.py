from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class SupImplementationAst(Ast, CompilerStages):
    tok_left_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceL))
    members: Seq[Asts.SupMemberAst] = field(default_factory=Seq)
    tok_right_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceR))

    @ast_printer_method
    @std.override_method
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

    @std.override_method
    def pre_process(self, context: PreProcessingContext) -> None:
        for member in self.members: member.pre_process(context)

    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.generate_top_level_scopes(scope_manager)

    @std.override_method
    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        for member in self.members: member.generate_top_level_aliases(scope_manager, **kwargs)

    @std.override_method
    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.load_super_scopes(scope_manager)

    @std.override_method
    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.postprocess_super_scopes(scope_manager)

    @std.override_method
    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.regenerate_generic_aliases(scope_manager)

    @std.override_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.regenerate_generic_types(scope_manager)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        for member in self.members: member.analyse_semantics(scope_manager, **kwargs)


__all__ = ["SupImplementationAst"]
