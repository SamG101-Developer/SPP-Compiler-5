from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LoopControlFlowStatementAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_seq_exit: Seq[TokenAst]
    skip_or_expr: Optional[ExpressionAst]

    def __post_init__(self) -> None:
        # Convert the exit tokens into a sequence.
        self.tok_seq_exit = Seq(self.tok_seq_exit)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_seq_exit.print(printer, " "),
            self.skip_or_expr.print(printer) if self.skip_or_expr else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        has_skip = isinstance(self.skip_or_expr, TokenAst) and self.skip_or_expr.token.token_type == TokenType.KwSkip
        if isinstance(self.skip_or_expr, (TokenAst, TypeAst)) and not has_skip:
            raise AstErrors.INVALID_EXPRESSION(self.skip_or_expr)

        # Get the number of control flow statement, and the loop's nesting level.
        number_of_controls = self.tok_seq_exit.length + (has_skip is True)
        nested_loop_depth  = kwargs["loop_count"]

        # Check the depth of the loop is greater than or equal to the number of control statements.
        if number_of_controls > nested_loop_depth:
            raise AstErrors.CONTROL_FLOW_TOO_MANY_CONTROLS(kwargs["loop_ast"], self, number_of_controls, nested_loop_depth)

        # Save and compare the loop's "exiting" type against other nested loop's exit statement types.
        if not isinstance(self.skip_or_expr, TokenAst):

            # Ensure the memory integrity of the expression.
            if self.skip_or_expr:
                self.skip_or_expr.analyse_semantics(scope_manager, **kwargs)
                AstMemoryHandler.enforce_memory_integrity(self.skip_or_expr, self.skip_or_expr, scope_manager, update_memory_info=False)

            # Infer the exit type of this loop control flow statement.
            match self.skip_or_expr:
                case None: exit_type = InferredType.from_type(CommonTypes.Void(self.tok_seq_exit[-1].pos))
                case _   : exit_type = self.skip_or_expr.infer_type(scope_manager, **kwargs)

            # Insert or check the depth's corresponding exit type.
            depth = nested_loop_depth - number_of_controls + 1
            if depth not in kwargs["loop_types"]:
                kwargs["loop_types"][depth] = (self.skip_or_expr or self.tok_seq_exit[-1], exit_type)
            else:
                that_expr, that_exit_type = kwargs["loop_types"][depth]
                if not exit_type.symbolic_eq(that_exit_type, scope_manager.current_scope):
                    raise AstErrors.TYPE_MISMATCH(that_expr, that_exit_type, self.skip_or_expr or self.tok_seq_exit[-1], exit_type)


__all__ = ["LoopControlFlowStatementAst"]
