from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


@dataclass
class GenericCompParameterRequiredAst(Asts.Ast, Asts.Mixins.OrderableAst):
    kw_cmp: Asts.TokenAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_cmp = self.kw_cmp or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwCmp)
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        self._variant = "Required"
        assert self.name is not None and self.type is not None

    def __eq__(self, other: GenericCompParameterRequiredAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericCompParameterRequiredAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_cmp.print(printer) + " ",
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Ensure the type does not have a convention.
        if (cs := self.type.get_conventions()).not_empty():
            raise SemanticErrors.InvalidConventionLocationError().add(
                cs[0], self.type, "comp generic parameter type").scopes(sm.current_scope)

        # Create a variable symbol for this constant in the current scope (class / function).
        symbol = VariableSymbol(
            name=Asts.IdentifierAst.from_type(self.name),
            type=self.type, visibility=Visibility.Public, is_generic=True)
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        sm.current_scope.add_symbol(symbol)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type of the default expression.
        self.type.analyse_semantics(sm)

        # Create the variable for the const parameter.
        ast = CodeInjection.inject_code(
            f"let {self.name}: {self.type}", SppParser.parse_let_statement_uninitialized, pos_adjust=self.pos)
        ast.analyse_semantics(sm, **kwargs)

        # Mark the symbol as initialized.
        symbol = sm.current_scope.get_symbol(Asts.IdentifierAst.from_type(self.name))
        symbol.memory_info.initialized_by(self)


__all__ = [
    "GenericCompParameterRequiredAst"]
