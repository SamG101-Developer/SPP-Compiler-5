from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


@dataclass
class GenericCompParameterOptionalAst(Ast, Ordered):
    tok_cmp: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwCmp))
    name: Asts.TypeAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    default: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        assert self.type
        assert self.default
        self._variant = "Optional"

    def __eq__(self, other: GenericCompParameterOptionalAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericCompParameterOptionalAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_cmp.print(printer) + " ",
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Ensure the type does not have a convention.
        if type(c := self.type.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.type, "comp generic parameter type").scopes(scope_manager.current_scope)

        # Create a variable symbol for this constant in the current scope (class / function).
        symbol = VariableSymbol(
            name=Asts.IdentifierAst.from_type(self.name),
            type=self.type, visibility=AstVisibility.Public, is_generic=True)
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        scope_manager.current_scope.add_symbol(symbol)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the default.
        if isinstance(self.default, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.default).scopes(scope_manager.current_scope)

        # Analyse the type of the default expression.
        self.type.analyse_semantics(scope_manager)
        self.default.analyse_semantics(scope_manager)

        # Make sure the default expression is of the correct type.
        default_type = self.default.infer_type(scope_manager)
        target_type = self.type
        if not target_type.symbolic_eq(default_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.name, target_type, self.default, default_type).scopes(scope_manager.current_scope)

        # Create the variable for the const parameter.
        ast = AstMutation.inject_code(f"let {self.name}: {self.type}", SppParser.parse_let_statement_uninitialized)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        symbol = scope_manager.current_scope.get_symbol(Asts.IdentifierAst.from_type(self.name))
        symbol.memory_info.initialized_by(self)


__all__ = ["GenericCompParameterOptionalAst"]
