from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


# Todo: a lot of kwargs["assignment"][0] is sen for getting symbols; check this because there can be > 1 in the
#  "assignment" list. Test multi-assignment or ban it if its a problem. would like to keep it though.


@dataclass(slots=True)
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

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.lhs, sep=", "),
            " " + self.op.print(printer) + " ",
            SequenceUtils.print(printer, self.rhs, sep=", ")]
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

        Mutability checks ensure that the left-hand-side is allowed to be mutated, and there are three different checks
        that can take place (depending on if the left-hand-side is a variable or attribute):
            1. For a variable, the symbol must be marked as "mut" (mutable), or never been initialized before.
            2. For a non-borrowed variable's attribute, the outermost symbol must be marked as "mut".
            3. For a borrowed variable's attribute, the outermost symbol must be a "&mut" (mutable) borrow.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: None.

        :raise SemanticErrors.MutabilityInvalidMutationError: This exception is raised if an immutable symbol is
            assigned to, or a partial assignment into an immutable borrow is attempted.
        :raise SemanticErrors.TypeMismatchError: This exception is raised if the right-hand side value's type does not
            match the corresponding left-hand side symbol's type.
        """

        # Ensure the LHS and RHS are semantically valid.
        for e in self.lhs:
            e.analyse_semantics(sm, **kwargs)

        for i, e in enumerate(self.rhs):
            if isinstance(e, Asts.PostfixExpressionAst) and isinstance(e.op, Asts.PostfixExpressionOperatorFunctionCallAst):
                kwargs |= {"inferred_return_type": self.lhs[i].infer_type(sm, **kwargs)}
            e.analyse_semantics(sm, **(kwargs | {"assignment": [self.lhs[i]]}))

        # Ensure the lhs targets are all symbolic (assignable to).
        lhs_syms = [sm.current_scope.get_variable_symbol_outermost_part(expr) for expr in self.lhs]
        if non_symbolic := [s for s in zip(lhs_syms, self.lhs) if not s[0]]:
            raise SemanticErrors.AssignmentInvalidLhsError().add(non_symbolic[0][1]).scopes(sm.current_scope)

        # For each assignment, check mutability, types compatibility, and resolve partial moves.
        for (lhs_expr, rhs_expr), lhs_sym in zip(zip(self.lhs, self.rhs), lhs_syms):

            # Full assignment (ie "x = y") requires the "x" symbol to be marked as "mut".
            if isinstance(lhs_expr, Asts.IdentifierAst) and not (lhs_sym.is_mutable or lhs_sym.memory_info.initialization_counter == 0):
                raise SemanticErrors.MutabilityInvalidMutationError().add(
                    lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization).scopes(sm.current_scope)

            # Attribute assignment (ie "x.y = z"), for a non-borrowed symbol, requires an outermost "mut" symbol.
            elif isinstance(lhs_expr, Asts.PostfixExpressionAst) and (not lhs_sym.memory_info.ast_borrowed and not lhs_sym.is_mutable):
                raise SemanticErrors.MutabilityInvalidMutationError().add(
                    lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization).scopes(sm.current_scope)

            # Attribute assignment (ie "x.y = z"), for a borrowed symbol, cannot contain an immutable borrow.
            elif isinstance(lhs_expr, Asts.PostfixExpressionAst) and lhs_sym.memory_info.is_borrow_ref:
                raise SemanticErrors.MutabilityInvalidMutationError().add(
                    lhs_sym.name, self.op, lhs_sym.memory_info.ast_borrowed).scopes(sm.current_scope)

            # Ensure the lhs and rhs have the same type.
            lhs_type = lhs_expr.infer_type(sm, **kwargs)
            rhs_type = rhs_expr.infer_type(sm, **kwargs)
            if not lhs_type.symbolic_eq(rhs_type, sm.current_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    lhs_sym.memory_info.ast_initialization, lhs_type, rhs_expr, rhs_type).scopes(sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        The memory checks for assignment statements fall under the following categories:
            1. Ensure the left-hand-side is initialized for an attribute initialization.
            2. Ensure the right-hand-side is initialized.
            3. Resolve moves if an identifier is set to a new value.
            4. Resolve partial moves if an attribute is set to a new value.

        The left-hand-side symbol may be non-initialized is the entire symbol is being set to a new value. This is how
        non-initialized/moved symbols become re-initialized with a new value. If the left-hand-side's direct outer
        symbol (of a target attribute) is non-initialized, then a single attribute cannot be set onto it, as it has no
        location in memory. For an attribute to be set a new value, the outermost variable must be initialized. For
        example, if "a.b.c = ..." is the assignment, then "a.b" must be initialized, ie "a" is initialized, and "a.b" is
        not in the partial moves list of the symbol for the variable "a".

        If a value has been set a new value, then mark this symbol as initialized, with this statement being the AST
        that most recently initialized it. Otherwise, an attribute has been set, so resolve this partial move (if it is
        a partial move) on the outermost symbol. If there is no outermost symbol, then the target is  "temporary" value,
        and as such requires no further action.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        # For each assignment, check the memory status and resolve any (partial-)moves.
        lhs_syms = [sm.current_scope.get_variable_symbol_outermost_part(expr) for expr in self.lhs]
        is_attr = lambda ast: not isinstance(ast, Asts.IdentifierAst)
        for (lhs_expr, rhs_expr), lhs_sym in zip(zip(self.lhs, self.rhs), lhs_syms):

            # Ensure the memory status of the left and right hand side.
            AstMemoryUtils.enforce_memory_integrity(lhs_sym.name.clone_at(lhs_expr.pos), self.op, sm, check_move=is_attr(lhs_expr), check_partial_move=False, mark_moves=False, check_pins=False)
            rhs_expr.check_memory(sm, **(kwargs | {"assignment": [lhs_expr]}))
            AstMemoryUtils.enforce_memory_integrity(rhs_expr, self.op, sm)
            if is_attr(lhs_expr):
                AstMemoryUtils.enforce_memory_integrity(lhs_expr.lhs, self.op, sm, check_partial_move=is_attr(lhs_expr.lhs), mark_moves=False, check_pins=False)

            # Extra check to prevent "let: Type" being assigned more than once (bypasses lack of "mut").
            if isinstance(lhs_expr, Asts.IdentifierAst) and not lhs_sym.is_mutable and lhs_sym.memory_info.initialization_counter == 1:
                raise SemanticErrors.MutabilityInvalidMutationError().add(
                    lhs_sym.name, self.op, lhs_sym.memory_info.ast_initialization).scopes(sm.current_scope)

            # Resolve moved identifiers to the "initialized" state.
            if not is_attr(lhs_expr):
                lhs_sym.memory_info.initialized_by(self)

            # Remove partial moves from their outermost symbol.
            elif is_attr(lhs_expr):
                lhs_sym.memory_info.remove_partial_move(lhs_expr)


__all__ = [
    "AssignmentStatementAst"]
