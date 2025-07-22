from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class LoopExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_loop: Asts.TokenAst = field(default=None)
    cond: Asts.LoopConditionAst = field(default=None)
    body: Asts.InnerScopeAst = field(default=None)
    else_block: Optional[Asts.LoopElseStatementAst] = field(default=None)

    _loop_type_info: dict[int, Asts.TypeAst] = field(default_factory=dict, init=False, repr=False)
    _loop_level: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_loop = self.kw_loop or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwLoop)

    def __hash__(self) -> int:
        return id(self)

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
        return self.cond.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Get the loop type set by exit expressions inside the loop.
        loop_type = self._loop_type_info.get(self._loop_level, (None, CommonTypes.Void(self.pos)))[1]

        # Check the else block's type if it exists and match it against the loop type.
        ignore_else = kwargs.pop("ignore_else", False)
        if self.else_block and not ignore_else:
            else_type = self.else_block.infer_type(sm, **kwargs)
            if not AstTypeUtils.symbolic_eq(loop_type, else_type, sm.current_scope, sm.current_scope):
                final_member = self.body.members[-1] if self.body.members else self.body.tok_r
                raise SemanticErrors.TypeMismatchError().add(self, loop_type, final_member, else_type).scopes(sm.current_scope)

        # If the return type is "Void", but the condition is compiler time "true", then the loop is infinite.
        # Todo: Change this to count "exits", as breaking with Void is possible
        if AstTypeUtils.symbolic_eq(loop_type, CommonTypesPrecompiled.VOID, sm.current_scope, sm.current_scope):
            if type(self.cond) is Asts.LoopConditionBooleanAst and type(self.cond.expr) is Asts.BooleanLiteralAst:
                if self.cond.expr.to_python_literal():
                    loop_type = CommonTypesPrecompiled.NEVER

        return loop_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Create a new scope for the loop body.
        sm.create_and_move_into_new_scope(f"<loop#{self.pos}>")
        self.cond.analyse_semantics(sm, **kwargs)

        # For the top level loop, set the count to 0, and create empty dictionaries for the loop types and ASTs.
        kwargs["loop_level"] = kwargs.get("loop_level", 0)
        kwargs["loop_types"] = kwargs.get("loop_types", {})
        kwargs["loop_ast"] = self

        # Save the loop AST into the ASTs dictionary, and save the type information for the type inference.
        self._loop_type_info = kwargs["loop_types"]
        self._loop_level = kwargs["loop_level"]

        # Analyse the loop body with an increased loop level.
        kwargs["loop_level"] += 1
        self.body.analyse_semantics(sm, **kwargs)

        # Analyse the else block if it exists.
        if self.else_block:
            self.else_block.analyse_semantics(sm, **kwargs)

        # Move out of the loop scope.
        sm.move_out_of_current_scope()

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Todo: Check twice (for memory move checks in a loop).
        #  for i in range(("loop_level" not in kwargs) + 1):

        sm.move_to_next_scope()

        # Check twice so that once-time invalidation fail on the second loop.
        tm = ScopeManager(sm.global_scope, sm.current_scope)
        for m in [tm, sm]:
            self.cond.check_memory(m, **(kwargs | {"loop_double_check": m is sm}))
            self.body.check_memory(m, **kwargs)

        if self.else_block:
            self.else_block.check_memory(sm, **kwargs)
        sm.move_out_of_current_scope()


__all__ = [
    "LoopExpressionAst"]
