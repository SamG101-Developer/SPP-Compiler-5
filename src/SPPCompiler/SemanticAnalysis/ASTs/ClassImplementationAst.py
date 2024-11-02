from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ClassMemberAst import ClassMemberAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ClassImplementationAst(Ast, Default, Stage1_PreProcessor, Stage2_SymbolGenerator, Stage4_SemanticAnalyser):
    tok_left_brace: TokenAst
    members: Seq[ClassMemberAst]
    tok_right_brace: TokenAst

    def __post_init__(self) -> None:
        # Convert the members into a sequence.
        self.members = Seq(self.members)

    def __deepcopy__(self, memodict={}):
        return ClassImplementationAst(
            self.pos, copy.deepcopy(self.tok_left_brace), copy.deepcopy(self.members),
            copy.deepcopy(self.tok_right_brace), _ctx=self._ctx, _scope=self._scope)

    @staticmethod
    def default() -> ClassImplementationAst:
        # Create a default class implementation AST.
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return ClassImplementationAst(-1, TokenAst.default(TokenType.TkBraceL), Seq(), TokenAst.default(TokenType.TkBraceR))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
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
        self.members.for_each(lambda m: m.pre_process(context))

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Generate the symbols for the members.
        self.members.for_each(lambda m: m.generate_symbols(scope_manager))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Analyse the semantics of the members.
        self.members.for_each(lambda m: m.analyse_semantics(scope_manager, **kwargs))

        # Check there are no duplicate attribute names.
        attribute_names = self.members.map_attr("name")
        if duplicate_attributes := attribute_names.non_unique():
            raise AstErrors.DUPLICATE_IDENTIFIER(duplicate_attributes[0][0], duplicate_attributes[0][1], "attribute")


__all__ = ["ClassImplementationAst"]
