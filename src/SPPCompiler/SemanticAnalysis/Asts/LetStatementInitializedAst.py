from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from llvmlite import ir as llvm

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class LetStatementInitializedAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_let: Asts.TokenAst = field(default=None)
    assign_to: Asts.LocalVariableAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_let = self.kw_let or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwLet)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        assert self.assign_to is not None and self.value is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_let.print(printer) + " ",
            self.assign_to.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.value).scopes(sm.current_scope)

        # Analyse the assign_to and value of the let statement.
        self.value.analyse_semantics(sm, **(kwargs | {"assignment": self.assign_to.extract_names}))
        AstMemoryUtils.enforce_memory_integrity(self.value, self.tok_assign, sm, update_memory_info=False)
        self.assign_to.analyse_semantics(sm, value=self.value, **kwargs)

    def generate_llvm_definitions(
            self, sm: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None,
            block: llvm.Block = None, **kwargs) -> Any:

        for var, val in self.assign_to._new_asts:
            # Get the type of the variable and allocate memory for it.
            var_type = sm.current_scope.get_symbol(var.name).type
            llvm_type = sm.current_scope.get_symbol(var_type).llvm_info.llvm_type
            llvm_alloc = builder.alloca(llvm_type, name=str(var.name))

            # Convert the value to an LLVM constant and store it in the allocated memory.
            llvm_value = val.generate_llvm_definitions(sm, llvm_module, None, None, **kwargs)
            llvm_var = llvm.Constant(llvm_type, llvm_value)
            builder.store(llvm_var, llvm_alloc)


__all__ = [
    "LetStatementInitializedAst"]
