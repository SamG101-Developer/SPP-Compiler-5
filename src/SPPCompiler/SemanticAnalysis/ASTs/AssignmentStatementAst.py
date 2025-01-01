from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class AssignmentStatementAst(Ast, TypeInferrable, CompilerStages):
    lhs: Seq[ExpressionAst]
    op: TokenAst
    rhs: Seq[ExpressionAst]

    def __post_init__(self) -> None:
        # Convert the lhs and rhs into a sequence.
        self.lhs = Seq(self.lhs)
        self.rhs = Seq(self.rhs)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer) + " ",
            self.op.print(printer) + " ",
            self.rhs.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import IdentifierAst, PostfixExpressionAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Ensure the LHS and RHS are semantically valid.
        for e in self.lhs: e.analyse_semantics(scope_manager, **kwargs)
        for e in self.rhs: e.analyse_semantics(scope_manager, **kwargs)

        # Ensure the lhs targets are all symbolic (assignable to).
        lhs_syms = self.lhs.map(lambda e: scope_manager.current_scope.get_variable_symbol_outermost_part(e))
        if non_symbolic := lhs_syms.zip(self.lhs).find(lambda s: not s[0]):
            raise SemanticErrors.AssignmentInvalidLhsError().add(non_symbolic[1])

        # For each assignment, check mutability, types compatibility, and resolve partial moves.
        for (lhs_expr, rhs_expr), lhs_sym in self.lhs.zip(self.rhs).zip(lhs_syms):

            # Ensure the memory status of the left and right hand side.
            AstMemoryHandler.enforce_memory_integrity(lhs_sym.name, self.op, scope_manager, check_move=False, check_partial_move=False, update_memory_info=False)
            AstMemoryHandler.enforce_memory_integrity(rhs_expr, self.op, scope_manager)

            # Full assignment (ie "x = y") requires the "x" symbol to be marked as "mut".
            if isinstance(lhs_expr, IdentifierAst) and not (lhs_sym.is_mutable or lhs_sym.memory_info.initialization_counter == 0):
                raise SemanticErrors.MutabilityInvalidMutationError().add(lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization)

            # Attribute assignment (ie "x.y = z"), for a non-borrowed symbol, requires an outermost "mut" symbol.
            elif isinstance(lhs_expr, PostfixExpressionAst) and (not lhs_sym.memory_info.ast_borrowed and not lhs_sym.is_mutable):
                raise SemanticErrors.MutabilityInvalidMutationError().add(lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization)

            # Attribute assignment (ie "x.y = z"), for a borrowed symbol, requires an outermost mutable borrow.
            elif isinstance(lhs_expr, PostfixExpressionAst) and (lhs_sym.memory_info.ast_borrowed and lhs_sym.memory_info.is_borrow_ref):
                raise SemanticErrors.MutabilityInvalidMutationError().add(lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization)

            # Ensure the lhs and rhs have the same type and convention (cannot do "Str = &Str" for example).
            lhs_type = lhs_expr.infer_type(scope_manager, **kwargs)
            rhs_type = rhs_expr.infer_type(scope_manager, **kwargs)
            if not lhs_type.symbolic_eq(rhs_type, scope_manager.current_scope):
                raise SemanticErrors.TypeMismatchError(lhs_sym.memory_info.ast_initialization, lhs_type, rhs_expr, rhs_type)

            # Resolve memory status, by marking lhs identifiers as initialized, or removing partial moves.
            if isinstance(lhs_expr, IdentifierAst):
                lhs_sym.memory_info.initialized_by(self)
            elif isinstance(lhs_expr, PostfixExpressionAst):
                lhs_sym.memory_info.remove_partial_move(lhs_expr)


__all__ = ["AssignmentStatementAst"]
