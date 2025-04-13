from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ClassImplementationAst(Asts.Ast):
    tok_left_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftCurlyBrace))
    members: Seq[Asts.ClassMemberAst] = field(default_factory=Seq)
    tok_right_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightCurlyBrace))

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

    @property
    def pos_end(self) -> int:
        return self.tok_right_brace.pos_end

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the members.
        for m in self.members: m.pre_process(ctx)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Generate the symbols for the members.
        for m in self.members: m.generate_top_level_scopes(sm)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Load the super scopes for the members.
        for m in self.members: m.load_super_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Pre analyse the members
        for m in self.members: m.pre_analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the semantics of the members.
        for m in self.members:
            m.analyse_semantics(sm, **kwargs)

        # Check there are no duplicate attribute names.
        attribute_names = self.members.map_attr("name")
        if duplicates := attribute_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "attribute").scopes(sm.current_scope)


__all__ = [
    "ClassImplementationAst"]
