from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class InnerScopeAst[T](Ast, Default, TypeInferrable, CompilerStages):
    tok_left_brace: TokenAst
    members: Seq[T]
    tok_right_brace: TokenAst

    def __post_init__(self) -> None:
        # Convert the members into a sequence.
        self.members = Seq(self.members)

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

    @staticmethod
    def default(body: Seq[T] = None) -> InnerScopeAst[T]:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return InnerScopeAst(-1, TokenAst.default(TokenType.TkBraceL), body or Seq(), TokenAst.default(TokenType.TkBraceR))

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

        # Return the last member's inferred type, if there are any members.
        if self.members:
            temp_manager = ScopeManager(scope_manager.global_scope, self._scope)
            return self.members[-1].infer_type(temp_manager, **kwargs)

        # An empty scope is inferred to have a void type.
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, inline: bool = False, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import LoopControlFlowStatementAst, RetStatementAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        self._scope = scope_manager.current_scope

        # Check there is no code after a "ret" statement, as this is unreachable.
        for i, member in self.members.enumerate():
            if isinstance(member, (LoopControlFlowStatementAst, RetStatementAst)) and member is not self.members[-1]:
                raise SemanticErrors.UnreachableCodeError().add(member, self.members[i + 1])

        # Analyse the semantics of each member.
        for m in self.members:
            m.analyse_semantics(scope_manager, **kwargs)
