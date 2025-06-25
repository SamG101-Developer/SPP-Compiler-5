from __future__ import annotations

import copy
from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.Utils.Sequence import SequenceUtils


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

    def __post_init__(self) -> None:
        self.tk_dot = self.tk_dot or Asts.TokenAst.raw(token_type=SppTokenType.TkDot)
        self.kw_res = self.kw_res or Asts.TokenAst.raw(token_type=SppTokenType.KwRes)
        self.function_argument_group = self.function_argument_group or Asts.FunctionCallArgumentGroupAst(pos=self.pos)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return "".join([
            self.tk_dot.print(printer),
            self.kw_res.print(printer),
            self.function_argument_group.print(printer)
        ])

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

        # Get the generator type.
        generator_type = lhs.infer_type(sm, **kwargs)
        generator_type, *_ = AstTypeUtils.get_generator_and_yielded_type(generator_type, sm, lhs, "resume expression")

        # Convert it into a "Generated" type (container for the yielded value).
        if AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GEN, generator_type.without_generics, sm.current_scope, sm.current_scope):
            new = "Generated"
        elif AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GEN_OPT, generator_type.without_generics, sm.current_scope, sm.current_scope):
            new = "GeneratedOpt"
        elif AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GEN_RES, generator_type.without_generics, sm.current_scope, sm.current_scope):
            new = "GeneratedRes"
        else:
            raise ValueError(f"The generator type must be a Gen, GenOpt or GenRes type. Got: {generator_type}.")

        generated_type = copy.deepcopy(generator_type)
        generated_type.type_parts[-1].value = new

        # Remove the "Send" parameter from the "Generated" type
        SequenceUtils.remove_if(generated_type.type_parts[-1].generic_argument_group.arguments, lambda x: x.name.type_parts[-1].value == "Send")
        generated_type.analyse_semantics(sm, **kwargs)

        # Return the generated type.
        return generated_type

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        """
        The key check for this AST is to ensure that the LHS is a generator type. This allows the `.resume()` to be
        called, and to ensure that the actual `Gen::resume` coroutine is called.

        :param sm: The scope manager.
        :param lhs: The left-hand side expression.
        :param kwargs: Additional keyword arguments.
        """

        # Check the LHS is a generator type (for specific error).
        lhs_type = lhs.infer_type(sm, **kwargs)
        AstTypeUtils.get_generator_and_yielded_type(lhs_type, sm, lhs, "resume expression")

        # Check the argument (send value) is valid, by passing it into the ".send" function call.
        member_access = Asts.PostfixExpressionOperatorMemberAccessAst.new_runtime(pos=self.tk_dot.pos, new_field=Asts.IdentifierAst(value="send"))
        member_access = Asts.PostfixExpressionAst(pos=self.pos, lhs=lhs, op=member_access)
        func_call = Asts.PostfixExpressionOperatorFunctionCallAst(function_argument_group=self.function_argument_group)
        func_call = Asts.PostfixExpressionAst(pos=self.pos, lhs=member_access, op=func_call)
        func_call.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        """
        Todo: does anything need to be done here?

        :param sm: The scope manager.
        :param lhs: The left-hand side expression.
        :param kwargs: Additional keyword arguments.
        """


__all__ = [
    "PostfixExpressionOperatorResumeCoroutineAst",
]
