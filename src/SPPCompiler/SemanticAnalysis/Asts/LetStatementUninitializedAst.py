from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class LetStatementUninitializedAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_let: Asts.TokenAst = field(default=None)
    assign_to: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_let = self.kw_let or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwLet)
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        assert self.assign_to is not None and self.type is not None

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
        # Analyse the variable's type.
        self.type.analyse_semantics(sm, **kwargs)

        # Check the type isn't the void type.
        void_type = CommonTypes.Void(self.pos)

        # Recursively analyse the variable.
        self.assign_to.analyse_semantics(sm, value=self.type, **kwargs)


__all__ = [
    "LetStatementUninitializedAst"]
