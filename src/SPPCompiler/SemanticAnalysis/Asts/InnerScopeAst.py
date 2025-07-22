from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class InnerScopeAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_l: Asts.TokenAst = field(default=None)
    members: list[Asts.StatementAst] = field(default_factory=list)
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

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:

        # Return the last member's inferred type, if there are any members.
        if self.members:
            temp_manager = ScopeManager(sm.global_scope, self._scope)
            return self.members[-1].infer_type(temp_manager, **kwargs)

        # An empty scope is inferred to have a void type.
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # sm.create_and_move_into_new_scope(f"<inner-scope#{self.pos}>")
        self._scope = sm.current_scope

        # Check there is no code after a "ret" statement, as this is unreachable.
        # Todo: this is inefficient; check from the last statement and work backwards.
        for i, member in enumerate(self.members):
            if isinstance(member, (Asts.LoopControlFlowStatementAst, Asts.RetStatementAst)) and member is not self.members[-1]:
                raise SemanticErrors.UnreachableCodeError().add(member, self.members[i + 1]).scopes(sm.current_scope)

        # Analyse the semantics of each member.
        for m in self.members:
            m.analyse_semantics(sm, **kwargs)

        # sm.move_out_of_current_scope()

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # sm.move_to_next_scope()

        # Check the memory of each member.
        for m in self.members:
            m.check_memory(sm, **kwargs)

        all_syms = sm.current_scope.all_symbols(exclusive=False)
        inner_syms = sm.current_scope.all_symbols(exclusive=True)

        # Invalidate yielded borrows that are linked.
        for sym in inner_syms:
            if type(sym) is not VariableSymbol: continue

            for pin in sym.memory_info.ast_pins.copy():
                pin_sym = sm.current_scope.get_symbol(pin)
                for info in pin_sym.memory_info.borrow_refers_to.copy():
                    SequenceUtils.remove_if(pin_sym.memory_info.borrow_refers_to, lambda x: x[0] == sym.name)
                    SequenceUtils.remove_if(pin_sym.memory_info.borrow_refers_to, lambda x: x[0] == info[0])

        for sym in all_syms:
            if type(sym) is not VariableSymbol: continue
            for bor in sym.memory_info.borrow_refers_to.copy():
                a, b, _, scope = bor
                if scope == sm.current_scope:
                    sym.memory_info.borrow_refers_to.remove(bor)

        # If the final expression of the inner scope is being used (ie assigned to outer variable), then memory check it.
        if (move := kwargs.get("assignment", False)) and self.members:
            last_member = self.members[-1]
            AstMemoryUtils.enforce_memory_integrity(
                last_member, move, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
                check_pins=True, check_pins_linked=True, mark_moves=True)

        # sm.move_out_of_current_scope()


__all__ = [
    "InnerScopeAst"]
