from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.WithExpressionAliasAst import WithExpressionAliasAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class WithExpressionAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_with: TokenAst
    alias: Optional[WithExpressionAliasAst]
    expression: ExpressionAst
    body: InnerScopeAst[StatementAst]

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_with.print(printer),
            self.alias.print(printer) if self.alias else "",
            self.expression.print(printer),
            self.body.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expression, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.expression)

        # Create a new scope for the with block and move into it.
        scope_manager.create_and_move_into_new_scope(f"<with:{self.pos}>")
        self.expression.analyse_semantics(scope_manager, **kwargs)

        # Check a Ctx type is superimposed over the type of the expression.
        expression_type = self.expression.infer_type(scope_manager, **kwargs).type
        expression_sup_types = scope_manager.current_scope.get_symbol(expression_type).scope.sup_scopes.map(lambda s: s.type_symbol.name)
        context_types = Seq([CommonTypes.CtxRef(), CommonTypes.CtxMut()]).map(TypeAst.without_generics)
        if not context_types.any(lambda t: expression_sup_types.any(lambda s: s.symbolic_eq(t, scope_manager.current_scope))):
            raise AstErrors.INVALID_WITH_EXPRESSION(self, self.expression)

        # Analyse the alias, if it exists.
        if self.alias:
            self.alias.analyse_semantics(scope_manager, **kwargs)

        # Analyse the body of the with expression and move out of the current scope.
        self.body.analyse_semantics(scope_manager, **kwargs)
        scope_manager.move_out_of_current_scope()


__all__ = ["WithExpressionAst"]
