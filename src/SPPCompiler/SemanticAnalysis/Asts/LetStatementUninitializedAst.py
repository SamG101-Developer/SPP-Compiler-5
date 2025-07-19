from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass(slots=True)
class LetStatementUninitializedAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_let: Asts.TokenAst = field(default=None)
    assign_to: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_let = self.kw_let or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwLet)
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = [
            self.kw_let.print(printer) + " ",
            self.assign_to.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Create a dummy object initializer for the variable.
        mock_init = Asts.ObjectInitializerAst(pos=self.type.pos, class_type=self.type)

        # Analyse the variable's type, and recursively analyse the variable.
        self.type.analyse_semantics(sm, **kwargs)
        self.assign_to.analyse_semantics(sm, value=mock_init, **(kwargs | {"from_non_init": True}))

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self.assign_to.check_memory(sm, **(kwargs | {"from_non_init": True}))


__all__ = [
    "LetStatementUninitializedAst"]
