from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True)
class LoopControlFlowStatementAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_seq_exit: list[Asts.TokenAst] = field(default_factory=list)
    skip_or_expr: Optional[Asts.ExpressionAst] = field(default=None)

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.tok_seq_exit, sep=" "),
            self.skip_or_expr.print(printer) if self.skip_or_expr else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.skip_or_expr.pos_end if self.skip_or_expr else self.tok_seq_exit[-1].pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Get the number of control flow statement, and the loop's nesting level.
        has_skip = type(self.skip_or_expr) is Asts.TokenAst and self.skip_or_expr.token_type == SppTokenType.KwSkip
        number_of_controls = len(self.tok_seq_exit) + (has_skip is True)
        nested_loop_depth  = kwargs["loop_level"]

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.skip_or_expr, (Asts.TokenAst, Asts.TypeAst)) and not has_skip:
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.skip_or_expr).scopes(sm.current_scope)

        # Check the depth of the loop is greater than or equal to the number of control statements.
        if number_of_controls > nested_loop_depth:
            raise SemanticErrors.LoopTooManyControlFlowStatementsError().add(
                kwargs["loop_ast"].kw_loop, self, number_of_controls, nested_loop_depth).scopes(sm.current_scope)

        # Save and compare the loop's "exiting" type against other nested loop's exit statement types.
        if not isinstance(self.skip_or_expr, Asts.TokenAst):

            # Ensure the memory integrity of the expression.
            if self.skip_or_expr:
                self.skip_or_expr.analyse_semantics(sm, **kwargs)

            # Infer the exit type of this loop control flow statement.
            match self.skip_or_expr:
                case None: exit_type = CommonTypes.Void(self.tok_seq_exit[-1].pos)
                case _   : exit_type = self.skip_or_expr.infer_type(sm, **kwargs)

            # Insert or check the depth's corresponding exit type.
            depth = nested_loop_depth - number_of_controls
            if depth not in kwargs["loop_types"]:
                kwargs["loop_types"][depth] = (self.skip_or_expr or self.tok_seq_exit[-1], exit_type)
            else:
                that_expr, that_exit_type = kwargs["loop_types"][depth]

                # Todo: should be 2 different scopes in case of a typedef inside 1 of the scopes
                if not AstTypeUtils.symbolic_eq(exit_type, that_exit_type, sm.current_scope, sm.current_scope):
                    raise SemanticErrors.TypeMismatchError().add(
                        that_expr, that_exit_type, self.skip_or_expr or self.tok_seq_exit[-1], exit_type).scopes(sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        if self.skip_or_expr:
            AstMemoryUtils.enforce_memory_integrity(
                self.skip_or_expr, self.skip_or_expr, sm, check_move=True, check_partial_move=True,
                check_move_from_borrowed_ctx=True, check_pins=True, check_pins_linked=True, mark_moves=True, **kwargs)


__all__ = [
    "LoopControlFlowStatementAst"]
