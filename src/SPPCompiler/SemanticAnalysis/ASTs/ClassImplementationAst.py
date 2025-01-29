from __future__ import annotations

import copy
import std
from dataclasses import dataclass, field
from typing import Dict, Self

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ClassImplementationAst(Ast, CompilerStages):
    tok_left_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceL))
    members: Seq[Asts.ClassMemberAst] = field(default_factory=Seq)
    tok_right_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceR))

    def __deepcopy__(self, memodict: Dict = None) -> ClassImplementationAst:
        return ClassImplementationAst(
            self.pos, self.tok_left_brace, copy.deepcopy(self.members),
            self.tok_right_brace, _ctx=self._ctx, _scope=self._scope)

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
        # Pre-process the members.
        for m in self.members: m.pre_process(context)

    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Generate the symbols for the members.
        for m in self.members: m.generate_top_level_scopes(scope_manager)

    @std.override_method
    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the super scopes for the members.
        for m in self.members: m.load_super_scopes(scope_manager)

    @std.override_method
    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Inject the super scopes for the members.
        for m in self.members: m.postprocess_super_scopes(scope_manager)

    @std.override_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Regenerate the generic types for the members.
        for m in self.members: m.regenerate_generic_types(scope_manager)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the semantics of the members.
        for m in self.members:
            m.analyse_semantics(scope_manager, **kwargs)

        # Check there are no duplicate attribute names.
        attribute_names = self.members.map_attr("name")
        if duplicates := attribute_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "attribute")


__all__ = ["ClassImplementationAst"]
