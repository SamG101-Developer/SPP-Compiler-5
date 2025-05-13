from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class PostfixExpressionOperatorIndexAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The PostfixExpressionOperatorIndexAst class represents an index operator over an expression. It looks like either
    "a[n]" or "a[mut n]" to get the mutable borrow of the index. The index operator is a runtime operator, so bounds are
    checked per function call.
    """

    tok_l: Asts.TokenAst = field(default=None)
    """The opening square bracket to depict the indexing operation."""

    kw_mut: Optional[Asts.TokenAst] = field(default=None)
    """The optional "mut" keyword to indicate a mutable borrow."""

    expr: Asts.ExpressionAst = field(default=None)
    """The expression that evaluates to the index value."""

    tok_r: Asts.TokenAst = field(default=None)
    """The closing square bracket to close the indexing operation."""

    _as_func: Optional[Asts.PostfixExpressionAst] = field(default=None, init=False, repr=False)
    """The function representation of the index expression."""

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(token_type=SppTokenType.TkLeftSquareBracket)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(token_type=SppTokenType.TkRightSquareBracket)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return "".join([
            self.tok_l.print(printer), self.kw_mut.print(printer) if self.kw_mut else "", self.expr.print(printer),
            self.tok_r.print(printer)])

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def infer_type(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        """
        The infer_type method is used to infer the type of the index expression. It uses the transformed AST to check
        for the return type of the `index_ref` or `index_mut` function.

        :param sm: The scope manager.
        :param lhs: The left-hand side expression.
        :param kwargs: Additional keyword arguments.
        :return: The return type of the index expression.
        """

        return self._as_func.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        """
        The check for the postfix indexing operator is to ensure that the LHS superimposes the `IndexRef` type for
        immutable indexing, and `IndexMut` for mutable indexing.

        Todo: this currently calls any "index_ref" or "index_mut" function, but it should be a check for the
          "IndexRef" or "IndexMut" traits.

        :param sm: The scope manager.
        :param lhs: The left-hand side expression.
        :param kwargs: Additional keyword arguments.
        """

        # Create a transformed AST that looks like: "lhs.index_ref" or "lhs.index_mut".
        index_type = Asts.IdentifierAst(pos=self.tok_l.pos, value="index_ref" if not self.kw_mut else "index_mut")
        index_field = Asts.PostfixExpressionOperatorMemberAccessAst.new_runtime(pos=self.pos, new_field=index_type)
        index_field = Asts.PostfixExpressionAst(pos=self.pos, lhs=lhs, op=index_field)

        # Create a transformed AST that looks like: "lhs.index_ref(expr)" or "lhs.index_mut(expr)".
        args = Asts.FunctionCallArgumentGroupAst(pos=self.pos, arguments=[Asts.FunctionCallArgumentUnnamedAst(pos=self.pos, value=self.expr)])
        index_call = Asts.PostfixExpressionOperatorFunctionCallAst(pos=self.pos, function_argument_group=args)
        index_call = Asts.PostfixExpressionAst(pos=self.pos, lhs=index_field, op=index_call)

        # Analyse the semantics of the transformed AST, ensuring that the function exists.
        index_call.analyse_semantics(sm, **kwargs)
        self._as_func = index_call

    def check_memory(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        self._as_func.check_memory(sm, **kwargs)


__all__ = [
    "PostfixExpressionOperatorIndexAst",
]
