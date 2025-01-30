from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LoopElseStatementAst(Ast, TypeInferrable):
    tok_else: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwElse))
    body: Asts.InnerScopeAst = field(default_factory=Asts.InnerScopeAst)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_else.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type from the body.
        return self.body.infer_type(scope_manager, **kwargs)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        scope_manager.create_and_move_into_new_scope(f"<loop-else:{self.pos}>")
        self.body.analyse_semantics(scope_manager, **kwargs)
        scope_manager.move_out_of_current_scope()


__all__ = ["LoopElseStatementAst"]
