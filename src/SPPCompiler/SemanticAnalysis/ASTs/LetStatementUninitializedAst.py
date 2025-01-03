from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LetStatementUninitializedAst(Ast, TypeInferrable, CompilerStages):
    tok_let: TokenAst
    assign_to: LocalVariableAst
    tok_colon: TokenAst
    type: TypeAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = [
            self.tok_let.print(printer) + " ",
            self.assign_to.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @staticmethod
    def from_variable_and_type(variable: LocalVariableAst, type: TypeAst) -> LetStatementUninitializedAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TokenAst
        return LetStatementUninitializedAst(variable.pos, TokenAst.default(TokenType.KwLet), variable, TokenAst.default(TokenType.TkColon), type)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Analyse the variable's type.
        self.type.analyse_semantics(scope_manager, **kwargs)

        # Check the type isn't the void type.
        void_type = CommonTypes.Void(self.pos)
        if self.type.symbolic_eq(void_type, scope_manager.current_scope):
            raise SemanticErrors.TypeVoidInvalidUsageError().add(self.type)

        # Recursively analyse the variable.
        self.assign_to.analyse_semantics(scope_manager, value=self.type, **kwargs)


__all__ = ["LetStatementUninitializedAst"]
