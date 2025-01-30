from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


@dataclass
class GenericCompParameterVariadicAst(Ast, Ordered):
    tok_cmp: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwCmp))
    tok_variadic: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkDblDot))
    name: Asts.TypeAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        assert self.type
        self._variant = "Variadic"

    @std.override_method
    def __eq__(self, other: GenericCompParameterVariadicAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericCompParameterVariadicAst) and self.name == other.name

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_cmp.print(printer) + " ",
            self.tok_variadic.print(printer),
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Create a variable symbol for this constant in the current scope (class / function).
        symbol = VariableSymbol(
            name=Asts.IdentifierAst.from_type(self.name),
            type=self.type, visibility=AstVisibility.Public, is_generic=True)
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        scope_manager.current_scope.add_symbol(symbol)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the type of the default expression.
        self.type.analyse_semantics(scope_manager)

        # Create the variable for the const parameter.
        ast = AstMutation.inject_code(f"let {self.name}: {self.type}", SppParser.parse_let_statement_uninitialized)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        symbol = scope_manager.current_scope.get_symbol(Asts.IdentifierAst.from_type(self.name))
        symbol.memory_info.initialized_by(self)


__all__ = ["GenericCompParameterVariadicAst"]
