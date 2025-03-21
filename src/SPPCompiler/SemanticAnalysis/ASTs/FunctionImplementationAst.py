from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from llvmlite import ir as llvm

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionImplementationAst(Ast):
    tok_left_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftCurlyBrace))
    members: Seq[Asts.FunctionMemberAst] = field(default_factory=Seq)
    tok_right_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightCurlyBrace))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.members:
            string = [
                self.tok_left_brace.print(printer) + "\n",
                self.members.print(printer, "\n"),
                self.tok_right_brace.print(printer) + "\n"]
        else:
            string = [
                self.tok_left_brace.print(printer),
                self.tok_right_brace.print(printer) + "\n"]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_right_brace.pos_end

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Check there is no code after a "ret" statement, as this is unreachable.
        for i, member in self.members.enumerate():
            if isinstance(member, (Asts.LoopControlFlowStatementAst, Asts.RetStatementAst)) and member is not self.members[-1]:
                raise SemanticErrors.UnreachableCodeError().add(member, self.members[i + 1]).scopes(scope_manager.current_scope)

        # Analyse each member of the class implementation.
        for m in self.members:
            m.analyse_semantics(scope_manager, **kwargs)

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        # Create an entry block to start the function.
        entry_block = llvm_function.append_basic_block(name="entry")
        builder = llvm.IRBuilder(entry_block)

        # Generate the LLVM definitions for each member of the class implementation.
        for member in self.members:
            member.generate_llvm_definitions(scope_handler, llvm_module, builder, entry_block, **kwargs)

        # Return the entry block to start the function.
        return entry_block


__all__ = ["FunctionImplementationAst"]
