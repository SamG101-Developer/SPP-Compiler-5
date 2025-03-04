from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LoopControlFlowStatementAst(Ast, TypeInferrable):
    tok_seq_exit: Seq[Asts.TokenAst] = field(default_factory=Seq)
    skip_or_expr: Optional[Asts.ExpressionAst] = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_seq_exit.print(printer, " ") + " " if self.tok_seq_exit else "",
            self.skip_or_expr.print(printer) if self.skip_or_expr else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        # All statements are inferred as "void".
        return InferredTypeInfo(CommonTypes.Void(self.pos))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        has_skip = isinstance(self.skip_or_expr, Asts.TokenAst) and self.skip_or_expr.token_type == SppTokenType.KwSkip
        if isinstance(self.skip_or_expr, (Asts.TokenAst, Asts.TypeAst)) and not has_skip:
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.skip_or_expr)

        # Get the number of control flow statement, and the loop's nesting level.
        number_of_controls = self.tok_seq_exit.length + (has_skip is True)
        nested_loop_depth  = kwargs["loop_level"]

        # Check the depth of the loop is greater than or equal to the number of control statements.
        if number_of_controls > nested_loop_depth:
            raise SemanticErrors.LoopTooManyControlFlowStatementsError().add(kwargs["loop_ast"], self, number_of_controls, nested_loop_depth)

        # Save and compare the loop's "exiting" type against other nested loop's exit statement types.
        if not isinstance(self.skip_or_expr, Asts.TokenAst):

            # Ensure the memory integrity of the expression.
            if self.skip_or_expr:
                self.skip_or_expr.analyse_semantics(scope_manager, **kwargs)
                AstMemoryHandler.enforce_memory_integrity(self.skip_or_expr, self.skip_or_expr, scope_manager, update_memory_info=False)

            # Infer the exit type of this loop control flow statement.
            match self.skip_or_expr:
                case None: exit_type = InferredTypeInfo(CommonTypes.Void(self.tok_seq_exit[-1].pos))
                case _   : exit_type = self.skip_or_expr.infer_type(scope_manager, **kwargs)

            # Insert or check the depth's corresponding exit type.
            depth = nested_loop_depth - number_of_controls
            if depth not in kwargs["loop_types"]:
                kwargs["loop_types"][depth] = (self.skip_or_expr or self.tok_seq_exit[-1], exit_type)
            else:
                that_expr, that_exit_type = kwargs["loop_types"][depth]

                # Todo: should be 2 different scopes in case of a typedef inside 1 of the scopes
                if not exit_type.symbolic_eq(that_exit_type, scope_manager.current_scope):
                    raise SemanticErrors.TypeMismatchError().add(that_expr, that_exit_type, self.skip_or_expr or self.tok_seq_exit[-1], exit_type)


__all__ = ["LoopControlFlowStatementAst"]
