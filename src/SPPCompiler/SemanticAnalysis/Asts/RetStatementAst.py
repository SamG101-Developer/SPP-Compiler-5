from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any

from llvmlite import ir as llvm

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass(slots=True)
class RetStatementAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_ret: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwRet))
    expr: Optional[Asts.ExpressionAst] = field(default=None)
    _func_ret_type: Optional[Asts.TypeAst] = field(default=None, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_ret.print(printer),
            f" {self.expr.print(printer)}" if self.expr is not None else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.expr.pos_end if self.expr else self.tok_ret.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Todo: allow returning from a coroutine if there is no expression attached to it (early return).

        # Check the enclosing function is a subroutine and not a coroutine.
        if kwargs["function_type"].token_type != SppTokenType.KwFun:
            raise SemanticErrors.FunctionCoroutineContainsReturnStatementError().add(
                kwargs["function_type"], self.tok_ret).scopes(sm.current_scope)
        self._func_ret_type = kwargs["function_ret_type"]

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expr:
            self.expr.analyse_semantics(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(self.expr, self.tok_ret, sm)
            expression_type = self.expr.infer_type(sm, **kwargs)
        else:
            expression_type = CommonTypes.Void(self.pos)

        # Determine the return type of the enclosing function.
        expected_type = kwargs["function_ret_type"]

        # Check the expression type matches the expected type.
        if not expected_type.symbolic_eq(expression_type, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                expression_type, expected_type, self.expr, expected_type).scopes(sm.current_scope)

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        # Create a return instruction with the expression if it exists.
        if self.expr:
            return_value = self.expr.generate_llvm_definitions(scope_handler, llvm_module, builder, block, **kwargs)
            builder.ret(return_value)
        else:
            builder.ret_void()
        return None


__all__ = [
    "RetStatementAst"]
