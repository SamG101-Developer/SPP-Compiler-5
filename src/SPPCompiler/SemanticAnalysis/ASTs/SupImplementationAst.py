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
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return SupImplementationAst(-1, TokenAst.default(TokenType.TkBraceL), members or Seq(), TokenAst.default(TokenType.TkBraceR))

    def pre_process(self, context: PreProcessingContext) -> None:
        self.members.for_each(lambda member: member.pre_process(context))

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        self.members.for_each(lambda member: member.generate_symbols(scope_manager))

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.members.for_each(lambda member: member.alias_types(scope_manager, **kwargs))

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        self.members.for_each(lambda member: member.load_sup_scopes(scope_manager))

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        self.members.for_each(lambda member: member.inject_sup_scopes(scope_manager))

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        self.members.for_each(lambda member: member.alias_types_regeneration(scope_manager))

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        self.members.for_each(lambda member: member.regenerate_generic_types(scope_manager))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.members.for_each(lambda m: m.analyse_semantics(scope_manager, **kwargs))


__all__ = ["SupImplementationAst"]
