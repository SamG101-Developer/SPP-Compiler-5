from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ClassImplementationAst(Ast):
    tok_left_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkBraceL))
    members: Seq[Asts.ClassMemberAst] = field(default_factory=Seq)
    tok_right_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkBraceR))

    def __deepcopy__(self, memodict: Dict = None) -> ClassImplementationAst:
        return ClassImplementationAst(
            self.pos, self.tok_left_brace, copy.deepcopy(self.members),
            self.tok_right_brace, _ctx=self._ctx, _scope=self._scope)

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
        # Pre-process the members.
        for m in self.members: m.pre_process(context)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Generate the symbols for the members.
        for m in self.members: m.generate_top_level_scopes(scope_manager)

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes for the members.
        for m in self.members: m.load_super_scopes(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the semantics of the members.
        for m in self.members:
            m.analyse_semantics(scope_manager, **kwargs)

        # Check there are no duplicate attribute names.
        attribute_names = self.members.map_attr("name")
        if duplicates := attribute_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "attribute")


__all__ = ["ClassImplementationAst"]
