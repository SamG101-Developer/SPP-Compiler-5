from __future__ import annotations
from dataclasses import dataclass, field
from llvmlite import ir as llvm
from typing import Optional, TYPE_CHECKING, Any

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class RetStatementAst(Ast, TypeInferrable, CompilerStages):
    tok_ret: TokenAst
    expression: Optional[ExpressionAst]
    _func_ret_type: Optional[TypeAst] = field(default=None, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_ret.print(printer),
            self.expression.print(printer) if self.expression is not None else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Check the enclosing function is a subroutine and not a coroutine.
        if kwargs["function_type"].token.token_type != SppTokenType.KwFun:
            raise SemanticErrors.FunctionCoroutineContainsReturnStatementError().add(kwargs["function_type"], self.tok_ret)
        self._func_ret_type = kwargs["function_ret_type"]

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expression:
            self.expression.analyse_semantics(scope_manager, **kwargs)
            expression_type = self.expression.infer_type(scope_manager, **kwargs)
        else:
            void_type = CommonTypes.Void(self.pos)
            expression_type = InferredType.from_type(void_type)

        # Determine the return type of the enclosing function.
        expected_type = InferredType.from_type(kwargs["function_ret_type"])

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
