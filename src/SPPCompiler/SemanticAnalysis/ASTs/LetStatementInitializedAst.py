from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from llvmlite import ir as llvm

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LetStatementInitializedAst(Ast, TypeInferrable, CompilerStages):
    let_keyword: TokenAst
    assign_to: LocalVariableAst
    assign_token: TokenAst
    value: ExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.let_keyword.print(printer) + " ",
            self.assign_to.print(printer) + " ",
            self.assign_token.print(printer) + " ",
            self.value.print(printer)]
        return "".join(string)

    @staticmethod
    def from_variable_and_value(variable: LocalVariableAst, value: ExpressionAst) -> LetStatementInitializedAst:
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        from SPPCompiler.SemanticAnalysis import TokenAst
        return LetStatementInitializedAst(
            variable.pos, TokenAst.default(SppTokenType.KwLet), variable,
            TokenAst.default(SppTokenType.TkAssign, pos=variable.pos), value)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (TokenAst, TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value)

        # Analyse the assign_to and value of the let statement.
        self.value.analyse_semantics(scope_manager, **(kwargs | {"assignment": self.assign_to.extract_names}))
        AstMemoryHandler.enforce_memory_integrity(
            self.value, self.assign_token, scope_manager, update_memory_info=False)
        self.assign_to.analyse_semantics(scope_manager, value=self.value, **kwargs)

    def generate_llvm_definitions(
            self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None,
            block: llvm.Block = None, **kwargs) -> Any:

        for var, val in self.assign_to._new_asts:
            # Get the type of the variable and allocate memory for it.
            var_type = scope_handler.current_scope.get_symbol(var.name).type
            llvm_type = scope_handler.current_scope.get_symbol(var_type).llvm_info.llvm_type
            llvm_alloc = builder.alloca(llvm_type, name=str(var.name))

            # Convert the value to an LLVM constant and store it in the allocated memory.
            llvm_value = val.generate_llvm_definitions(scope_handler, llvm_module, None, None, **kwargs)
            llvm_var = llvm.Constant(llvm_type, llvm_value)
            builder.store(llvm_var, llvm_alloc)


__all__ = ["LetStatementInitializedAst"]
