from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class WithExpressionAst(Ast, TypeInferrable):
    tok_with: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwWith))
    alias: Optional[Asts.WithExpressionAliasAst] = field(default=None)
    expression: Asts.ExpressionAst = field(default=None)
    body: Asts.InnerScopeAst = field(default_factory=lambda: Asts.InnerScopeAst())

    def __post_init__(self) -> None:
        assert self.expression

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_with.print(printer),
            self.alias.print(printer) if self.alias else "",
            self.expression.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        return self.body.infer_type(scope_manager, **kwargs)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expression, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.expression)

        # Create a new scope for the with block and move into it.
        scope_manager.create_and_move_into_new_scope(f"<with:{self.pos}>")
        self.expression.analyse_semantics(scope_manager, **kwargs)

        # Check a Ctx type is superimposed over the type of the expression.
        expression_type = self.expression.infer_type(scope_manager, **kwargs).type
        expression_sup_types = scope_manager.current_scope.get_symbol(expression_type).scope.sup_scopes
        expression_sup_types = expression_sup_types.filter(lambda s: isinstance(s._ast, Asts.ClassPrototypeAst))
        expression_sup_types = expression_sup_types.map(lambda s: s.type_symbol.fq_name.without_generics())

        context_types = Seq([CommonTypes.CtxRef(), CommonTypes.CtxMut()]).map(Asts.TypeAst.without_generics)
        if not context_types.any(lambda t: expression_sup_types.any(lambda s: s.symbolic_eq(t, scope_manager.current_scope))):
            raise SemanticErrors.WithExpressionNonContextualConditionError().add(self.expression)

        # Analyse the alias, if it exists.
        if self.alias:
            self.alias.analyse_semantics(scope_manager, with_expression=self.expression, **kwargs)

        # Analyse the body of the with expression and move out of the current scope.
        self.body.analyse_semantics(scope_manager, **kwargs)
        scope_manager.move_out_of_current_scope()


__all__ = ["WithExpressionAst"]
