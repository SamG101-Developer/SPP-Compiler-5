from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class AssignmentStatementAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The AssignmentStatementAst class is an AST node that represents an assignment statement. This AST can be used to
    assign n values at once, including Pythons "a, b = b, a" syntax. The assignment operator is always the "=" token.
    There must be an equal number of expressions on the left and right hand side.
    
    Example:

    .. code-block:: S++

        x, y = y, 100
    """
    
    lhs: Seq[Asts.ExpressionAst] = field(default_factory=Seq)
    """The sequence of lhs targets."""

    op: Asts.TokenAst = field(default=None)
    """The ``=`` operator."""

    rhs: Seq[Asts.ExpressionAst] = field(default_factory=Seq)
    """The sequence of rhs values to assign to the targets."""

    def __post_init__(self) -> None:
        self.op = self.op or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        assert self.lhs.not_empty() and self.rhs.not_empty()

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer) + " ",
            self.op.print(printer) + " ",
            self.rhs.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.rhs[-1].pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        The assignment statement returns a ``Void`` type, because no value can be returned out of an assignment. For
        example, with ``x = y``, ``y`` is moved into ``x``, and allowing access to ``x`` outside of the assignment means
        either ``x`` is being moved again (invalidating it), or it is being borrowed implicitly, breaking memory rules.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The `std::void::Void` type.
        """

        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        An AssignmentStatementAst must have a symbolic left-hand-side. This ensures that the left-hand-side is
        non-temporary, and has a valid location in memory for assignment. The types must match between the left and
        right hand side, and the memory status of the right hand side must be valid.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: None.

        :raise SemanticErrors.MutabilityInvalidMutationError: This exception is raised if an immutable symbol is
            assigned to, or a partial assignment into an immutable borrow is attempted.
        :raise SemanticErrors.TypeMismatchError: This exception is raised if the right-hand side value's type does not
            match the corresponding left-hand side symbol's type.
        """

        # Ensure the LHS and RHS are semantically valid.
        for e in self.lhs: e.analyse_semantics(sm, **kwargs)
        for e in self.rhs: e.analyse_semantics(sm, **kwargs)

        # Ensure the lhs targets are all symbolic (assignable to).
        lhs_syms = self.lhs.map(lambda e: sm.current_scope.get_variable_symbol_outermost_part(e))
        if non_symbolic := lhs_syms.zip(self.lhs).find(lambda s: not s[0]):
            raise SemanticErrors.AssignmentInvalidLhsError().add(non_symbolic[1]).scopes(sm.current_scope)

        # For each assignment, check mutability, types compatibility, and resolve partial moves.
        for (lhs_expr, rhs_expr), lhs_sym in self.lhs.zip(self.rhs).zip(lhs_syms):

            # Ensure the memory status of the left and right hand side.
            # Todo: is the left-hand-side memory check required? all the flags are False, so it seems redundant.
            AstMemoryUtils.enforce_memory_integrity(lhs_sym.name, self.op, sm, check_move=False, check_partial_move=False, update_memory_info=False)
            AstMemoryUtils.enforce_memory_integrity(rhs_expr, self.op, sm)

            # Full assignment (ie "x = y") requires the "x" symbol to be marked as "mut".
            if isinstance(lhs_expr, Asts.IdentifierAst) and not (lhs_sym.is_mutable or lhs_sym.memory_info.initialization_counter == 0):
                raise SemanticErrors.MutabilityInvalidMutationError().add(
                    lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization).scopes(sm.current_scope)

            # Attribute assignment (ie "x.y = z"), for a non-borrowed symbol, requires an outermost "mut" symbol.
            elif isinstance(lhs_expr, Asts.PostfixExpressionAst) and (not lhs_sym.memory_info.ast_borrowed and not lhs_sym.is_mutable):
                raise SemanticErrors.MutabilityInvalidMutationError().add(
                    lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization).scopes(sm.current_scope)

            # Attribute assignment (ie "x.y = z"), for a borrowed symbol, cannot contain an immutable borrow.
            elif isinstance(lhs_expr, Asts.PostfixExpressionAst) and (immutable := lhs_sym.name.infer_type(sm, **kwargs).get_conventions().find(lambda c: type(c) is Asts.ConventionRefAst)):
                raise SemanticErrors.MutabilityInvalidMutationError().add(
                    lhs_sym.name, self.op, immutable).scopes(sm.current_scope)

            # Ensure the lhs and rhs have the same type and convention (cannot do "Str = &Str" for example).
            lhs_type = lhs_expr.infer_type(sm, **kwargs)
            rhs_type = rhs_expr.infer_type(sm, **kwargs)
            if not lhs_type.symbolic_eq(rhs_type, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    lhs_sym.memory_info.ast_initialization, lhs_type, rhs_expr, rhs_type).scopes(sm.current_scope)

            # Resolve memory status, by marking lhs identifiers as initialized, or removing partial moves.
            if isinstance(lhs_expr, Asts.IdentifierAst):
                lhs_sym.memory_info.initialized_by(self)
            elif isinstance(lhs_expr, Asts.PostfixExpressionAst):
                lhs_sym.memory_info.remove_partial_move(lhs_expr)


__all__ = [
    "AssignmentStatementAst"]
