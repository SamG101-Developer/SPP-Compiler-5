from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ClassAttributeAst(Ast, VisibilityEnabled):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    name: Asts.IdentifierAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        assert self.type

    def __deepcopy__(self, memodict: Dict = None) -> ClassAttributeAst:
        return ClassAttributeAst(
            self.pos, self.annotations, copy.deepcopy(self.name), self.tok_colon,
            copy.deepcopy(self.type), _visibility=self._visibility, _ctx=self._ctx, _scope=self._scope)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the annotations of this attribute.
        for a in self.annotations:
            a.pre_process(self)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Ensure the attribute type does not have a convention.
        if type(c := self.type.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.type, "attribute type").scopes(scope_manager.current_scope)

        # Create a variable symbol for this attribute in the current scope (class).
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility[0])
        scope_manager.current_scope.add_symbol(symbol)

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Type checks must be done before semantic analysis, as other ASTs may use this attribute prior to its analysis.
        self.type.analyse_semantics(scope_manager)

        # Ensure the attribute type is not void.
        void_type = CommonTypes.Void(self.pos)
        if self.type.symbolic_eq(void_type, scope_manager.current_scope):
            raise SemanticErrors.TypeVoidInvalidUsageError().add(self.type).scopes(scope_manager.current_scope)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:

        # Analyse the semantics of the annotations and the type of the attribute.
        for a in self.annotations:
            a.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ClassAttributeAst"]
