from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import copy, std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts


@dataclass
class ClassAttributeAst(Ast, VisibilityEnabled, CompilerStages):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    name: Asts.IdentifierAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        assert self.type

    def __deepcopy__(self, memodict={}):
        return ClassAttributeAst(
            self.pos, self.annotations, copy.deepcopy(self.name), self.tok_colon,
            copy.deepcopy(self.type), _visibility=self._visibility, _ctx=self._ctx, _scope=self._scope)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @std.override_method
    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the annotations of this attribute.
        for a in self.annotations:
            a.pre_process(self)

    @std.override_method
    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Create a variable symbol for this attribute in the current scope (class).
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility[0])
        scope_manager.current_scope.add_symbol(symbol)

    @std.override_method
    def postprocess_super_scopes(self, scope_manager: ScopeManager) -> None:
        self.type.analyse_semantics(scope_manager)

    @std.override_method
    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        self.type.analyse_semantics(scope_manager)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:

        # Analyse the semantics of the annotations and the type of the attribute.
        for a in self.annotations:
            a.analyse_semantics(scope_manager, **kwargs)

        # Ensure the attribute type is not void.
        void_type = CommonTypes.Void(self.pos)
        if self.type.symbolic_eq(void_type, scope_manager.current_scope):
            raise SemanticErrors.TypeVoidInvalidUsageError().add(self.type)


__all__ = ["ClassAttributeAst"]
