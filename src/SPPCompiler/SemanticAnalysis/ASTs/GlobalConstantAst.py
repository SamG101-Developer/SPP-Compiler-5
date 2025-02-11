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
    tok_cmp: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwCmp))
    name: Asts.IdentifierAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkAssign))
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

    def pre_process(self, context: PreProcessingContext) -> None:
        for a in self.annotations:
            a.pre_process(self)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Create a type symbol for this type in the current scope (class / function).
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility[0])
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        scope_manager.current_scope.add_symbol(symbol)

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        self.type.analyse_semantics(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value)

        # Analyse the type and value.
        self.type.analyse_semantics(scope_manager, **kwargs)
        self.value.analyse_semantics(scope_manager, **kwargs)

        # Check the value's type is the same as the type.
        expected_type = self.type
        given_type = self.value.infer_type(scope_manager, **kwargs)

        if not expected_type.symbolic_eq(given_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.type, expected_type, self.value, given_type)


__all__ = ["GlobalConstantAst"]
