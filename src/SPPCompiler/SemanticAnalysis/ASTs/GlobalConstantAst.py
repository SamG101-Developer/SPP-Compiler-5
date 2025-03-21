from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class GlobalConstantAst(Ast, VisibilityEnabled):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    tok_cmp: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwCmp))
    name: Asts.IdentifierAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        assert self.type
        assert self.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.tok_cmp.print(printer) + " ",
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.value.print(printer) + "\n"]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the annotations.
        for a in self.annotations:
            a.pre_process(self)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(scope_manager)

        # Ensure the old type does not have a convention.
        if type(c := self.type.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.type, "global constant type").scopes(scope_manager.current_scope)

        # Create a type symbol for this type in the current scope (class / function).
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility[0])
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        scope_manager.current_scope.add_symbol(symbol)

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        self.type.analyse_semantics(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the annotations.
        for a in self.annotations:
            a.analyse_semantics(scope_manager, **kwargs)

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value).scopes(scope_manager.current_scope)

        # Analyse the type and value.
        self.type.analyse_semantics(scope_manager, **kwargs)
        self.value.analyse_semantics(scope_manager, **kwargs)

        # Check the value's type is the same as the type.
        expected_type = self.type
        given_type = self.value.infer_type(scope_manager, **kwargs)

        if not expected_type.symbolic_eq(given_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.type, expected_type, self.value, given_type).scopes(scope_manager.current_scope)


__all__ = ["GlobalConstantAst"]
