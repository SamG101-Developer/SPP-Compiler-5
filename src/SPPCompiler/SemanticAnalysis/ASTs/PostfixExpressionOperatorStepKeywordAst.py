from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class PostfixExpressionOperatorStepKeywordAst(Ast, TypeInferrable):
    tok_dot: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkDot))
    tok_step: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwStep))

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_dot.print(printer),
            self.tok_step.print(printer)]
        return "".join(string)

    def is_runtime_access(self) -> bool:
        return True

    def is_static_access(self) -> bool:
        return False

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> InferredType:
        # Next operations return the "Gen" generic parameter's argument.
        function_return_type = lhs.infer_type(scope_manager, **kwargs).type.types[-1].generic_argument_group["Gen"].value
        return InferredType.from_type(function_return_type)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Todo: Check for superimposition, not direct equality
        # Check the iterable is a generator type.
        target_type = Seq([CommonTypes.GenMov(), CommonTypes.GenMut(), CommonTypes.GenRef()]).map(Asts.TypeAst.without_generics).map(InferredType.from_type)
        return_type = lhs.infer_type(scope_manager, **kwargs)
        if not target_type.any(lambda t: t.symbolic_eq(return_type.without_generics(), scope_manager.current_scope)):
            raise SemanticErrors.ExpressionNotGeneratorError().add(lhs, return_type.type, "next expression")

        # Tie borrows to coroutine pin outputs, for auto invalidation.
        if "assignment" in kwargs:
            # If the coroutine is symbolic (saved to a variable/attribute), then borrows can be tied to it.
            # Todo: only do this for borrow convention coroutines.
            if coroutine_symbol := scope_manager.current_scope.get_symbol(lhs):

                # Invalidate the previously yielded borrow from this coroutine.
                if coroutine_symbol.memory_info.pin_target.not_empty():
                    current_borrow = coroutine_symbol.memory_info.pin_target.pop(0)
                    current_borrow_symbol = scope_manager.current_scope.get_symbol(current_borrow)
                    current_borrow_symbol.memory_info.ast_moved = self.tok_step

                # Attach the new borrow to the coroutine's memory information.
                coroutine_symbol.memory_info.pin_target.append(kwargs["assignment"][0])


__all__ = ["PostfixExpressionOperatorStepKeywordAst"]
