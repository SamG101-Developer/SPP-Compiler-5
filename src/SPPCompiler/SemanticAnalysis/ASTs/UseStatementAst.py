from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementNamespaceReductionAst import UseStatementNamespaceReductionAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementTypeAliasAst import UseStatementTypeAliasAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UseStatementAst(Ast, VisibilityEnabled, TypeInferrable, CompilerStages):
    annotations: Seq[AnnotationAst]
    tok_use: TokenAst
    body: UseStatementNamespaceReductionAst | UseStatementTypeAliasAst

    def __post_init__(self) -> None:
        # Convert the annotations into a sequence.
        self.annotations = Seq(self.annotations)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.tok_use.print(printer) + " ",
            self.body.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the annotations of this use statement.
        self.annotations.for_each(lambda a: a.pre_process(self))
        self.body.pre_process(context)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        self.body.generate_symbols(scope_manager)  # , visibility=self._visibility)

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.body.alias_types(scope_manager, **kwargs)

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        self.body.load_sup_scopes(scope_manager)

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        self.body.inject_sup_scopes(scope_manager)

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        self.body.alias_types_regeneration(scope_manager)

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        self.body.regenerate_generic_types(scope_manager)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.body.analyse_semantics(scope_manager)


__all__ = ["UseStatementAst"]
