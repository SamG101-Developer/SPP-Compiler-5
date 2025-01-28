from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class WithExpressionAliasAst(Ast, CompilerStages):
    variable: Asts.LocalVariableAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkAssign))

    def __post_init__(self) -> None:
        assert self.variable

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer) + " ",
            self.tok_assign.print(printer)]
        return "".join(string)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, with_expression: Asts.ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser

        # Convert the call into the "Ctx[Mut|Ref].enter()" call.
        code = f"let {self.variable} = {with_expression}.enter()"
        let_ast = AstMutation.inject_code(code, SppParser.parse_let_statement_initialized)
        let_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["WithExpressionAliasAst"]
