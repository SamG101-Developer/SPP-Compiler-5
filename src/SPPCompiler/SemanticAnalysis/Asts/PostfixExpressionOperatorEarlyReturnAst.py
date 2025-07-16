from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class PostfixExpressionOperatorEarlyReturnAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_qst: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_qst = self.tok_qst or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkQuestionMark)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_qst.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_qst.pos_end

    def infer_type(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        lhs_type = lhs.infer_type(sm, **kwargs)
        lhs_scope = sm.current_scope.get_symbol(lhs_type).scope

        # Find the superimposition of "std:;ops::try::Try", and grab the residual type.
        for super_scope in [lhs_scope] + lhs_scope.sup_scopes:
            if type(super_scope._ast) is Asts.ClassPrototypeAst:
                if AstTypeUtils.symbolic_eq(super_scope.type_symbol.fq_name.without_generics, CommonTypesPrecompiled.TRY, super_scope, sm.current_scope):
                    return super_scope.type_symbol.fq_name.type_parts[-1].generic_argument_group["Output"].value

        raise

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        lhs_type = lhs.infer_type(sm, **kwargs)
        lhs_scope = sm.current_scope.get_symbol(lhs_type).scope

        # Ensure the lhs superimposes the "std::ops::try::Try" type.
        try_type = None
        for super_scope in [lhs_scope] + lhs_scope.sup_scopes:
            if type(super_scope._ast) is Asts.ClassPrototypeAst:
                if AstTypeUtils.symbolic_eq(super_scope.type_symbol.fq_name.without_generics, CommonTypesPrecompiled.TRY, super_scope, sm.current_scope):
                    try_type = super_scope.type_symbol.fq_name
                    break

        # Raise an error as the Try type is not found.
        if try_type is None:
            raise SemanticErrors.EarlyReturnRequiresTryTypeError().add(self, lhs, lhs_type).scopes(sm.current_scope)

        # Check the Residual type is compatible with the function's return type.
        residual_type = try_type.type_parts[-1].generic_argument_group["Residual"].value
        if not AstTypeUtils.symbolic_eq(kwargs["function_ret_type"][0], residual_type, kwargs["function_scope"], sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                kwargs["function_ret_type"][0], kwargs["function_ret_type"][0], lhs, residual_type).scopes(
                kwargs["function_scope"], sm.current_scope)


__all__ = [
    "PostfixExpressionOperatorEarlyReturnAst"]
