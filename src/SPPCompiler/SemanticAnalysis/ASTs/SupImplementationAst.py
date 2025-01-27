from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.SupMemberAst import SupMemberAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class SupImplementationAst(Ast, Default, CompilerStages):
    tok_left_brace: TokenAst
    members: Seq[SupMemberAst]
    tok_right_brace: TokenAst

    def __post_init__(self) -> None:
        # Convert the members into a sequence.
        self.members = Seq(self.members)

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

    @staticmethod
    def default(members: Seq[SupMemberAst] = None) -> SupImplementationAst:
        # Create a default class implementation AST.
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return SupImplementationAst(-1, TokenAst.default(SppTokenType.TkBraceL), members or Seq(), TokenAst.default(SppTokenType.TkBraceR))

    def pre_process(self, context: PreProcessingContext) -> None:
        for member in self.members: member.pre_process(context)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.generate_top_level_scopes(scope_manager)

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        for member in self.members: member.generate_top_level_aliases(scope_manager, **kwargs)

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.load_super_scopes(scope_manager)

    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.postprocess_super_scopes(scope_manager)

    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.regenerate_generic_aliases(scope_manager)

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        for member in self.members: member.regenerate_generic_types(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        for member in self.members: member.analyse_semantics(scope_manager, **kwargs)


__all__ = ["SupImplementationAst"]
