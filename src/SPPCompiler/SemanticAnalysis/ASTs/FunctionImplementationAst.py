from __future__ import annotations
from dataclasses import dataclass
from llvmlite import ir as llvm
from typing import TYPE_CHECKING, Any

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionMemberAst import FunctionMemberAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionImplementationAst(Ast, Default, CompilerStages):
    tok_left_brace: TokenAst
    members: Seq[FunctionMemberAst]
    tok_right_brace: TokenAst

    def __post_init__(self) -> None:
        # Convert the members into a sequence.
        self.members = Seq(self.members)

    @staticmethod
    def default() -> FunctionImplementationAst:
        # Create a default class implementation AST.
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        return FunctionImplementationAst(-1, TokenAst.default(SppTokenType.TkBraceL), Seq(), TokenAst.default(SppTokenType.TkBraceR))

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

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import LoopControlFlowStatementAst, RetStatementAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Check there is no code after a "ret" statement, as this is unreachable.
        for i, member in self.members.enumerate():
            if isinstance(member, (LoopControlFlowStatementAst, RetStatementAst)) and member is not self.members[-1]:
                raise SemanticErrors.UnreachableCodeError().add(member, self.members[i + 1])

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
