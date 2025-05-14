from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True)
class PostfixExpressionOperatorResumeCoroutineAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The PostfixExpressionOperatorResumeCoroutineAst class represents the resume coroutine operator over an expression.
    The operator is a special keyword, rather than a standard function call to `.resume()`, so that the compiler knows
    to type check against the `Yield` generic parameter of the generator object, rather than just fetching the
    generator.

    A value can be sent into the coroutine by giving it as an argument between the `()` parentheses. The value is
    passed to the coroutine as the return value of the last `gen` statement. The coroutine will then yield the next
    value in the generator.

    Todo: use this keyword to ensure the return type is actually Yield | None => safety for when coroutine has finished
    """

    tk_dot: Asts.TokenAst = field(default=None)
    """The dot operator to allow the field name to be provided."""

    kw_res: Asts.TokenAst = field(default=None)
    """The res keyword that indicates the resume coroutine operation."""

    function_argument_group: Asts.FunctionCallArgumentGroupAst = field(default=None)
    """The function arguments to be passed to the coroutine."""

    _as_func: Asts.PostfixExpressionAst = field(default=None, init=False, repr=False)
    """The function representation of the resume expression."""

    def __post_init__(self) -> None:
        self.kw_res = self.kw_res or Asts.TokenAst.raw(token_type=SppTokenType.KwRes)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return " ".join([self.kw_res.print(printer), self.function_argument_group.print(printer)])

    @property
    def pos_end(self) -> int:
        return self.function_argument_group.pos_end

    def infer_type(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        """
        The infer_type method is used to infer the type of the resume coroutine expression. It uses the transformed AST
        (the generator `.resume` function call) to infer the return type of the coroutine, and then extracts the `Yield`
        generic argument's value from it. This is guaranteed to exist, from the semantic analysis check.

        :param sm: The scope manager.
        :param lhs: The left-hand side expression.
        :param kwargs: Additional keyword arguments.
        :return: The return type of the resume coroutine expression.
        """

        func_ret_type = self._as_func.infer_type(sm, **kwargs)
        func_ret_type.analyse_semantics(sm, **kwargs)
        gen_type, yield_type = AstTypeUtils.get_generator_and_yielded_type(func_ret_type, sm, lhs, "resume expression")
        return yield_type

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        """
        The key check for this AST is to ensure that the LHS is a generator type. This allows the `.resume()` to be
        called, and to ensure that the actual `Gen::resume` coroutine is called. The function argument group is analysed
        part of the transformed AST, not in this AST.

        :param sm: The scope manager.
        :param lhs: The left-hand side expression.
        :param kwargs: Additional keyword arguments.
        """

        # Check the LHS is a generator type (for specific error).
        lhs_type = lhs.infer_type(sm, **kwargs)
        AstTypeUtils.get_generator_and_yielded_type(lhs_type, sm, lhs, "resume expression")

        # Create a transformed AST that looks like: "lhs.resume".
        resume_identifier = Asts.IdentifierAst(pos=self.kw_res.pos, value="resume")
        resume_field = Asts.PostfixExpressionOperatorMemberAccessAst.new_runtime(pos=self.pos, new_field=resume_identifier)
        resume_field = Asts.PostfixExpressionAst(pos=self.pos, lhs=lhs, op=resume_field)

        # Create a transformed AST that looks like: "lhs.resume(expr)".
        resume_call = Asts.PostfixExpressionOperatorFunctionCallAst(pos=self.pos, function_argument_group=self.function_argument_group)
        resume_call = Asts.PostfixExpressionAst(pos=self.pos, lhs=resume_field, op=resume_call)

        # Analyse the semantics of the transformed AST, ensuring that the function exists.
        resume_call.analyse_semantics(sm, **kwargs)
        self._as_func = resume_call

    def check_memory(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        """
        The additional "is_coro_resume" is required because any call to a coroutine will trigger the pinning logic.
        The exception is resuming a coroutine, because this would pin the yielded values themselves, which means they
        aren't assignable to anything.

        :param sm: The scope manager.
        :param lhs: The left-hand side expression.
        :param kwargs: Additional keyword arguments.
        """

        self._as_func.check_memory(sm, is_coro_resume=True, **kwargs)


__all__ = [
    "PostfixExpressionOperatorResumeCoroutineAst",
]
