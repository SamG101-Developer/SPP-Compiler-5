from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True)
class LoopElseStatementAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_else: Asts.TokenAst = field(default=None)
    body: Asts.InnerScopeAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_else = self.tok_else or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwElse)
        assert self.body is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_else.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type from the body.
        return self.body.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        sm.create_and_move_into_new_scope(f"<loop-else:{self.pos}>")
        self.body.analyse_semantics(sm, **kwargs)
        sm.move_out_of_current_scope()


__all__ = [
    "LoopElseStatementAst"]
