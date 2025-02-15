from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any

from llvmlite import ir as llvm

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class RetStatementAst(Ast, TypeInferrable):
    tok_ret: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwRet))
    expression: Optional[Asts.ExpressionAst] = field(default=None)
    _func_ret_type: Optional[Asts.TypeAst] = field(default=None, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_ret.print(printer),
            self.expression.print(printer) if self.expression is not None else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        # All statements are inferred as "void".
        return InferredTypeInfo(CommonTypes.Void(self.pos))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Check the enclosing function is a subroutine and not a coroutine.
        if kwargs["function_type"].token.token_type != SppTokenType.KwFun:
            raise SemanticErrors.FunctionCoroutineContainsReturnStatementError().add(kwargs["function_type"], self.tok_ret)
        self._func_ret_type = kwargs["function_ret_type"]

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expression:
            self.expression.analyse_semantics(scope_manager, **kwargs)
            expression_type = self.expression.infer_type(scope_manager, **kwargs)
        else:
            expression_type = InferredTypeInfo(CommonTypes.Void(self.pos))

        # Determine the return type of the enclosing function.
        expected_type = InferredTypeInfo(kwargs["function_ret_type"])

        # Check the expression type matches the expected type.
        if not expected_type.symbolic_eq(expression_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(expression_type.type, expected_type, self.expression, expected_type)

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        # Create a return instruction with the expression if it exists.
        if self.expression:
            return_value = self.expression.generate_llvm_definitions(scope_handler, llvm_module, builder, block, **kwargs)
            builder.ret(return_value)
        else:
            builder.ret_void()
        return None


__all__ = ["RetStatementAst"]
