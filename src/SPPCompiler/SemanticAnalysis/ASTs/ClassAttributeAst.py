from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage3_SupScopeLoader import Stage3_SupScopeLoader
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class ClassAttributeAst(Ast, VisibilityEnabled, Stage1_PreProcessor, Stage2_SymbolGenerator, Stage3_SupScopeLoader, Stage4_SemanticAnalyser):
    annotations: Seq[AnnotationAst]
    name: IdentifierAst
    tok_colon: TokenAst
    type: TypeAst

    def __post_init__(self) -> None:
        # Convert the annotations into a sequence.
        self.annotations = Seq(self.annotations)

    def __deepcopy__(self, memodict={}):
        return ClassAttributeAst(
            self.pos, copy.deepcopy(self.annotations), copy.deepcopy(self.name), copy.deepcopy(self.tok_colon),
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
        self.annotations.for_each(lambda a: a.pre_process(self))

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Create a variable symbol for this attribute in the current scope (class).
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility)
        scope_manager.current_scope.add_symbol(symbol)

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        ...

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        self.type.analyse_semantics(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Analyse the semantics of the annotations and the type of the attribute.
        self.annotations.for_each(lambda a: a.analyse_semantics(scope_manager, **kwargs))

        # Ensure the attribute type is not void.
        void_type = CommonTypes.Void(self.pos)
        if self.type.symbolic_eq(void_type, scope_manager.current_scope):
            raise AstErrors.INVALID_VOID_USE(self.type)


__all__ = ["ClassAttributeAst"]
