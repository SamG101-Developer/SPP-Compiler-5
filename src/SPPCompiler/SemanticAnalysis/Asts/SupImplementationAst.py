from __future__ import annotations

from dataclasses import dataclass, field

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
class SupImplementationAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    members: Seq[Asts.SupMemberAst] = field(default_factory=Seq)
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

    def pre_process(self, ctx: PreProcessingContext) -> None:
        for member in self.members: member.pre_process(ctx)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        for member in self.members: member.generate_top_level_scopes(sm)

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        for member in self.members: member.generate_top_level_aliases(sm, **kwargs)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        for member in self.members: member.qualify_types(sm, **kwargs)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        for member in self.members: member.load_super_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        for member in self.members: member.pre_analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        for member in self.members: member.analyse_semantics(sm, **kwargs)

    def code_gen(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        for member in self.members: member.code_gen(sm, llvm_module, **kwargs)


__all__ = [
    "SupImplementationAst"]
