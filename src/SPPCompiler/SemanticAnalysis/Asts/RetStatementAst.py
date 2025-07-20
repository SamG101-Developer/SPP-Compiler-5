from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


# from llvmlite import ir as llvm


@dataclass(slots=True)
class RetStatementAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_ret: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwRet))
    expr: Optional[Asts.ExpressionAst] = field(default=None)
    _func_ret_type: Optional[Asts.TypeAst] = field(default=None, init=False, repr=False)

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_ret.print(printer),
            f" {self.expr.print(printer)}" if self.expr is not None else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.expr.pos_end if self.expr else self.kw_ret.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.expr, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.expr).scopes(sm.current_scope)

        # Check the enclosing function is a subroutine and not a coroutine.
        if kwargs["function_type"].token_type != SppTokenType.KwFun and self.expr:
            raise SemanticErrors.FunctionCoroutineContainsReturnStatementError().add(
                kwargs["function_type"], self.expr).scopes(sm.current_scope)

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expr:
            if isinstance(self.expr, Asts.PostfixExpressionAst) and isinstance(self.expr.op, Asts.PostfixExpressionOperatorFunctionCallAst):
                kwargs |= {"inferred_return_type": kwargs["function_ret_type"][0]}

            self.expr.analyse_semantics(sm, **kwargs)
            expression_type = self.expr.infer_type(sm, **kwargs)
        else:
            expression_type = CommonTypesPrecompiled.VOID

        if kwargs["function_ret_type"]:
            # If the function return type has been given (function, method) then get and store it.
            self._func_ret_type = kwargs["function_ret_type"][0]
        else:
            # If there is no function return type, then this is the first return statement for a lambda, so store the type.
            self._func_ret_type = expression_type
            kwargs["function_ret_type"].append(self._func_ret_type)
            kwargs["function_scope"] = sm.current_scope

        # Do a type check on the return expression vs the expected returning type.
        expected_type = kwargs["function_ret_type"][0]
        if kwargs["function_type"].token_type == SppTokenType.KwFun:
            if not AstTypeUtils.symbolic_eq(expected_type, expression_type, kwargs["function_scope"], sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    expression_type, expression_type, self.expr, expected_type).scopes(
                    kwargs["function_scope"], sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Check the memory of the expression if it exists.
        if self.expr:
            self.expr.check_memory(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(
                self.expr, self.kw_ret, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
                check_pins=True, check_pins_linked=True, mark_moves=True, **kwargs)

    # def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
    #     # Create a return instruction with the expression if it exists.
    #     if self.expr:
    #         return_value = self.expr.generate_llvm_definitions(scope_handler, llvm_module, builder, block, **kwargs)
    #         builder.ret(return_value)
    #     else:
    #         builder.ret_void()
    #     return None


__all__ = [
    "RetStatementAst"]
