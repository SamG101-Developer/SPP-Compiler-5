from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


# from llvmlite import ir as llvm


@dataclass(slots=True)
class FunctionImplementationAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    members: Seq[Asts.FunctionMemberAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftCurlyBrace)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightCurlyBrace)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.members:
            string = [
                self.tok_l.print(printer) + "\n",
                SequenceUtils.print(printer, self.members, sep="\n"),
                self.tok_r.print(printer) + "\n"]
        else:
            string = [
                self.tok_l.print(printer),
                self.tok_r.print(printer) + "\n"]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check there is no code after a "ret" statement, as this is unreachable.
        for i, member in enumerate(self.members):
            if isinstance(member, (Asts.LoopControlFlowStatementAst, Asts.RetStatementAst)) and member is not self.members[-1]:
                raise SemanticErrors.UnreachableCodeError().add(member, self.members[i + 1]).scopes(sm.current_scope)

        # Analyse each member of the class implementation.
        for m in self.members:
            m.analyse_semantics(sm, **kwargs)

    # def generate_llvm_definitions(self, sm: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
    #     # Create an entry block to start the function.
    #     entry_block = llvm_function.append_basic_block(name="entry")
    #     builder = llvm.IRBuilder(entry_block)
    #
    #     # Generate the LLVM definitions for each member of the class implementation.
    #     for member in self.members:
    #         member.generate_llvm_definitions(sm, llvm_module, builder, entry_block, **kwargs)
    #
    #     # Return the entry block to start the function.
    #     return entry_block


__all__ = [
    "FunctionImplementationAst"]
