from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from llvmlite import ir as llvm

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LetStatementInitializedAst(Ast, TypeInferrable):
    let_keyword: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwLet))
    assign_to: Asts.LocalVariableAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.assign_to
        assert self.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.let_keyword.print(printer) + " ",
            self.assign_to.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.value.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value)

        # Analyse the assign_to and value of the let statement.
        self.value.analyse_semantics(scope_manager, **(kwargs | {"assignment": self.assign_to.extract_names}))
        AstMemoryHandler.enforce_memory_integrity(
            self.value, self.tok_assign, scope_manager, update_memory_info=False)
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
