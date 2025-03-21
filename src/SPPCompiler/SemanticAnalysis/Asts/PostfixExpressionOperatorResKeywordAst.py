from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class PostfixExpressionOperatorResKeywordAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_dot: Asts.TokenAst = field(default=None)
    tok_res: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_dot = self.tok_dot or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDot)
        self.tok_res = self.tok_res or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwRes)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_dot.print(printer),
            self.tok_res.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_res.pos_end

    def is_runtime_access(self) -> bool:
        return True

    def is_static_access(self) -> bool:
        return False

    def infer_type(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Next operations return the "Gen" generic parameter's argument.
        return lhs.infer_type(sm, **kwargs).type_parts()[0].generic_argument_group["Yield"].value

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Todo: Check for superimposition, not direct equality

        # Check the iterable is a generator type.
        ret_type = lhs.infer_type(sm, **kwargs)
        if not ret_type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATOR, sm.current_scope):
            raise SemanticErrors.ExpressionNotGeneratorError().add(
                lhs, ret_type, "next expression").scopes(sm.current_scope)

        # Tie borrows to coroutine pin outputs, for auto invalidation.
        if "assignment" in kwargs:

            # If the coroutine is symbolic (saved to a variable/attribute), then borrows can be tied to it.
            if coroutine_symbol := sm.current_scope.get_variable_symbol_outermost_part(lhs):

                # Invalidate old generated borrow and attach the new borrow to the coroutine's memory information.
                for old_pin_link in coroutine_symbol.memory_info.pin_links:
                    sm.current_scope.get_symbol(old_pin_link).memory_info.moved_by(self.tok_res)
                coroutine_symbol.memory_info.pin_links = kwargs["assignment"]


__all__ = [
    "PostfixExpressionOperatorResKeywordAst"]
