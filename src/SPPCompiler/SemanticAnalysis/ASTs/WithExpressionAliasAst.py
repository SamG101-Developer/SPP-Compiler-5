from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class WithExpressionAliasAst(Ast, CompilerStages):
    variable: LocalVariableAst
    tok_assign: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer) + " ",
            self.tok_assign.print(printer)]
        return "".join(string)

    def analyse_semantics(self, scope_manager: ScopeManager, with_expression: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Convert the call into the "Ctx[Mut|Ref].enter()" call.
        code = f"let {self.variable} = {with_expression}.enter()"
        let_ast = AstMutation.inject_code(code, Parser.parse_let_statement_initialized)
        let_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["WithExpressionAliasAst"]
