from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage3_SupScopeLoader import Stage3_SupScopeLoader
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GlobalConstantAst(Ast, VisibilityEnabled, Stage1_PreProcessor, Stage2_SymbolGenerator, Stage3_SupScopeLoader, Stage4_SemanticAnalyser):
    annotations: Seq[AnnotationAst]
    tok_cmp: TokenAst
    name: IdentifierAst
    tok_colon: TokenAst
    type: TypeAst
    tok_assign: TokenAst
    value: ExpressionAst

    def __post_init__(self) -> None:
        # Convert the annotations into a sequence.
        self.annotations = Seq(self.annotations)

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
        self.annotations.for_each(lambda a: a.pre_process(self))

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Create a type symbol for this type in the current scope (class / function).
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility)
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = True
        symbol.memory_info.initialized_by(self)
        scope_manager.current_scope.add_symbol(symbol)

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.value)

        # Analyse the type and value.
        self.type.analyse_semantics(scope_manager, **kwargs)
        self.value.analyse_semantics(scope_manager, **kwargs)

        # Check the value's type is the same as the type.
        expected_type = InferredType.from_type(self.type)
        given_type = self.value.infer_type(scope_manager, **kwargs)
        if not expected_type.symbolic_eq(given_type, scope_manager.current_scope):
            raise AstErrors.TYPE_MISMATCH(self.name, self.type, self.value, given_type.type)


__all__ = ["GlobalConstantAst"]
