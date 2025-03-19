from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LetStatementUninitializedAst(Ast, TypeInferrable):
    tok_let: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwLet))
    assign_to: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.assign_to
        assert self.type

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = [
            self.tok_let.print(printer) + " ",
            self.assign_to.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the variable's type.
        self.type.analyse_semantics(scope_manager, **kwargs)

        # Check the type isn't the void type.
        void_type = CommonTypes.Void(self.pos)
        if self.type.symbolic_eq(void_type, scope_manager.current_scope):
            raise SemanticErrors.TypeVoidInvalidUsageError().add(self.type).scopes(scope_manager.current_scope)

        # Recursively analyse the variable.
        self.assign_to.analyse_semantics(scope_manager, value=self.type, **kwargs)


__all__ = ["LetStatementUninitializedAst"]
