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


@dataclass(slots=True)
class GenericCompParameterOptionalAst(Asts.Ast, Asts.Mixins.OrderableAst):
    kw_cmp: Asts.TokenAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    default: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_cmp = self.kw_cmp or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwCmp)
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        assert self.name is not None and self.type is not None and self.default is not None
        self._variant = "Optional"

    def __eq__(self, other: GenericCompParameterOptionalAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericCompParameterOptionalAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_cmp.print(printer) + " ",
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.default.pos_end

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Ensure the type does not have a convention.
        if c := self.type.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.type, "comp generic parameter type").scopes(sm.current_scope)

        # Create a variable symbol for this constant in the current scope (class / function).
        symbol = VariableSymbol(
            name=Asts.IdentifierAst.from_type(self.name),
            type=self.type, visibility=Visibility.Public, is_generic=True)
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        sm.current_scope.add_symbol(symbol)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the default.
        if isinstance(self.default, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.default).scopes(sm.current_scope)

        # Analyse the type of the default expression.
        self.type.analyse_semantics(sm, **kwargs)
        self.default.analyse_semantics(sm, **kwargs)

        # Make sure the default expression is of the correct type.
        default_type = self.default.infer_type(sm)
        target_type = self.type
        if not target_type.symbolic_eq(default_type, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                self.name, target_type, self.default, default_type).scopes(sm.current_scope)

        # Create the variable for the const parameter.
        ast = CodeInjection.inject_code(
            f"let {self.name}: {self.type}", SppParser.parse_let_statement_uninitialized, pos_adjust=self.pos)
        ast.analyse_semantics(sm, **kwargs)

        # Mark the symbol as initialized.
        symbol = sm.current_scope.get_symbol(Asts.IdentifierAst.from_type(self.name))
        symbol.memory_info.initialized_by(self)


__all__ = [
    "GenericCompParameterOptionalAst"]
