from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class InnerScopeAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_l: Asts.TokenAst = field(default=None)
    members: Seq[Asts.StatementAst] = field(default_factory=Seq)
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
                self.members.print(printer, "\n"),
                self.tok_r.print(printer) + "\n"]
        else:
            string = [
                self.tok_l.print(printer),
                self.tok_r.print(printer) + "\n"]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:

        # Return the last member's inferred type, if there are any members.
        if self.members:
            temp_manager = ScopeManager(sm.global_scope, self._scope)
            return self.members[-1].infer_type(temp_manager, **kwargs)

        # An empty scope is inferred to have a void type.
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self._scope = sm.current_scope

        # Check there is no code after a "ret" statement, as this is unreachable.
        # Todo: this is inefficient; check from the last statement and work backwards.
        for i, member in self.members.enumerate():
            if isinstance(member, (Asts.LoopControlFlowStatementAst, Asts.RetStatementAst)) and member is not self.members[-1]:
                raise SemanticErrors.UnreachableCodeError().add(member, self.members[i + 1]).scopes(sm.current_scope)

        # Analyse the semantics of each member.
        for m in self.members:
            m.analyse_semantics(sm, **kwargs)


__all__ = [
    "InnerScopeAst"]
