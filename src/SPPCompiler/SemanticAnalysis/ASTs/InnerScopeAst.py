from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class InnerScopeAst(Ast, TypeInferrable):
    tok_left_brace: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftCurlyBrace))
    members: Seq[Asts.StatementAst] = field(default_factory=Seq)
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

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:

        # Return the last member's inferred type, if there are any members.
        if self.members:
            temp_manager = ScopeManager(scope_manager.global_scope, self._scope)
            return self.members[-1].infer_type(temp_manager, **kwargs)

        # An empty scope is inferred to have a void type.
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, scope_manager: ScopeManager, inline: bool = False, **kwargs) -> None:
        self._scope = scope_manager.current_scope

        # Check there is no code after a "ret" statement, as this is unreachable.
        # Todo: this is inefficient; check from the last statement and work backwards.
        for i, member in self.members.enumerate():
            if isinstance(member, (Asts.LoopControlFlowStatementAst, Asts.RetStatementAst)) and member is not self.members[-1]:
                raise SemanticErrors.UnreachableCodeError().add(member, self.members[i + 1])

        # Analyse the semantics of each member.
        for m in self.members:
            m.analyse_semantics(scope_manager, **kwargs)


__all__ = ["InnerScopeAst"]
