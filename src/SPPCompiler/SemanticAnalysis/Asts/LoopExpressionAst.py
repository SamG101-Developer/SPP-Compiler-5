from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class LoopExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_loop: Asts.TokenAst = field(default=None)
    cond: Asts.LoopConditionAst = field(default=None)
    body: Asts.InnerScopeAst = field(default=None)
    else_block: Optional[Asts.LoopElseStatementAst] = field(default=None)

    _loop_type_info: dict = field(default_factory=dict, init=False, repr=False)
    _loop_level: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_loop = self.kw_loop or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwLoop)
        assert self.cond is not None and self.body is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_loop.print(printer) + " ",
            self.cond.print(printer) + " ",
            self.body.print(printer) + "\n",
            self.else_block.print(printer) if self.else_block else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.else_block.pos_end if self.else_block else self.body.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Get the loop type set by exit expressions inside the loop.
        loop_type = self._loop_type_info.get(self._loop_level, (None, None))[1]
        if loop_type is None:
            return CommonTypes.Void(self.pos)

        # Check the else block's type if it exists and match it against the loop type.
        if self.else_block:
            else_type = self.else_block.infer_type(sm, **kwargs)
            if not loop_type.symbolic_eq(else_type, sm.current_scope):
                final_member = self.body.members[-1] if self.body.members else self.body.tok_r
                raise SemanticErrors.TypeMismatchError().add(self, loop_type, final_member, else_type).scopes(sm.current_scope)

        return loop_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Create a new scope for the loop body.
        sm.create_and_move_into_new_scope(f"<loop:{self.pos}>")
        self.cond.analyse_semantics(sm, **kwargs)

        # Todo: Analyse twice (for memory checks).
        # for i in range(("loop_level" not in kwargs) + 1):

        # For the top level loop, set the count to 0, and create empty dictionaries for the loop types and ASTs.
        kwargs["loop_level"] = kwargs.get("loop_level", 0)
        kwargs["loop_types"] = kwargs.get("loop_types", {})
        kwargs["loop_ast"] = self

        # Save the loop AST into the ASTs dictionary, and save the type information for the type inference.
        self._loop_type_info = kwargs["loop_types"]
        self._loop_level = kwargs["loop_level"]

        # Analyse the loop body and reduce the loop count.
        kwargs["loop_level"] += 1
        self.body.analyse_semantics(sm, **kwargs)

        # Analyse the else block if it exists.
        if self.else_block:
            self.else_block.analyse_semantics(sm, **kwargs)

        # Move out of the loop scope.
        sm.move_out_of_current_scope()


__all__ = [
    "LoopExpressionAst"]
