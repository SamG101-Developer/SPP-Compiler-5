from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionOperatorResKeywordAst(Ast, TypeInferrable):
    tok_dot: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkDot))
    tok_res: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwRes))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_dot.print(printer),
            self.tok_res.print(printer)]
        return "".join(string)

    def is_runtime_access(self) -> bool:
        return True

    def is_static_access(self) -> bool:
        return False

    def infer_type(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Next operations return the "Gen" generic parameter's argument.
        return lhs.infer_type(scope_manager, **kwargs).type_parts()[0].generic_argument_group["Yield"].value

    def analyse_semantics(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Todo: Check for superimposition, not direct equality

        # Check the iterable is a generator type.
        return_type = lhs.infer_type(scope_manager, **kwargs)
        if not return_type.without_generics().symbolic_eq(CommonTypes.Gen().without_generics(), scope_manager.current_scope):
            raise SemanticErrors.ExpressionNotGeneratorError().add(lhs, return_type, "next expression").scopes(scope_manager.current_scope)

        # Tie borrows to coroutine pin outputs, for auto invalidation.
        if "assignment" in kwargs:
            # If the coroutine is symbolic (saved to a variable/attribute), then borrows can be tied to it.
            # Todo: only do this for borrow convention coroutines.
            if coroutine_symbol := scope_manager.current_scope.get_variable_symbol_outermost_part(lhs):

                # Invalidate the previously yielded borrow from this coroutine.
                if coroutine_symbol.memory_info.pin_target.not_empty():
                    current_borrow = coroutine_symbol.memory_info.pin_target.pop(0)
                    current_borrow_symbol = scope_manager.current_scope.get_symbol(current_borrow)
                    current_borrow_symbol.memory_info.moved_by(self.tok_res)

                # Attach the new borrow to the coroutine's memory information.
                coroutine_symbol.memory_info.pin_target.append(kwargs["assignment"][0])


__all__ = ["PostfixExpressionOperatorResKeywordAst"]
