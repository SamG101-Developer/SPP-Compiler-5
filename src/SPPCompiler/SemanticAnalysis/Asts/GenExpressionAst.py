from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


# Todo: test in lambdas
# Todo: test "cor || { ... }"


@dataclass(slots=True)
class GenExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_gen: Asts.TokenAst = field(default=None)
    kw_with: Optional[Asts.TokenAst] = field(default=None)
    convention: Optional[Asts.ConventionAst] = field(default=None)
    expr: Optional[Asts.ExpressionAst] = field(default=None)

    _func_ret_type: Optional[Asts.TypeAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_gen = self.kw_gen or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwGen)

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_gen.print(printer) + " ",
            (self.kw_with.print(printer) + " ") if self.kw_with else "",
            self.convention.print(printer) if self.convention else "",
            self.expr.print(printer) if self.expr else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.expr.pos_end if self.expr else self.kw_gen.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # The inferred type of a gen expression is the type of the value being sent back into the coroutine.
        generator_type = self._func_ret_type
        send_type = generator_type.type_parts[0].generic_argument_group["Send"].value
        return send_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check the enclosing function is a coroutine and not a subroutine.
        if kwargs["function_type"].token_type != SppTokenType.KwCor:
            raise SemanticErrors.FunctionSubroutineContainsGenExpressionError().add(kwargs["function_type"], self.kw_gen).scopes(sm.current_scope)

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expr:
            if isinstance(self.expr, Asts.PostfixExpressionAst) and isinstance(self.expr.op, Asts.PostfixExpressionOperatorFunctionCallAst):
                gen_type, yield_type = AstTypeUtils.get_generator_and_yielded_type(
                    kwargs["function_ret_type"][0], sm, kwargs["function_ret_type"][0], "coroutine")
                kwargs |= {"inferred_return_type": kwargs["function_ret_type"][0] if self.kw_with else yield_type}

            self.expr.analyse_semantics(sm, **kwargs)
            expression_type = self.expr.infer_type(sm, **kwargs).with_convention(self.convention)
        else:
            expression_type = CommonTypesPrecompiled.VOID

        if kwargs["function_ret_type"]:
            # If the function return type has been given (function, method) then get and store it.
            self._func_ret_type = kwargs["function_ret_type"][0]
        else:
            # If there is no function return type, then this is the first return statement for a lambda, so store the type.
            self._func_ret_type = CommonTypes.Gen(self.expr.pos, expression_type, CommonTypesPrecompiled.VOID)
            self._func_ret_type.analyse_semantics(sm, **kwargs)
            kwargs["function_ret_type"].append(self._func_ret_type)
            kwargs["function_scope"] = sm.current_scope

        # Determine the yield type of the enclosing function.
        gen_type, yield_type = AstTypeUtils.get_generator_and_yielded_type(
            kwargs["function_ret_type"][0], sm, kwargs["function_ret_type"][0], "coroutine")

        # Check the expression type matches the expected type.
        if not self.kw_with and not AstTypeUtils.symbolic_eq(yield_type, expression_type, kwargs["function_scope"], sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(yield_type, yield_type, expression_type, expression_type).scopes(sm.current_scope)

        # If the "with" keyword is being used, the expression type must be a Gen type that matches the function_ret_type.
        if self.kw_with and not AstTypeUtils.symbolic_eq(kwargs["function_ret_type"][0], expression_type, sm.current_scope, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(kwargs["function_ret_type"][0], kwargs["function_ret_type"][0], self.expr, expression_type).scopes(kwargs["function_scope"], sm.current_scope)

        # Apply the function argument law of exclusivity checks to the expression.
        if self.expr:
            ast = Asts.FunctionCallArgumentGroupAst(
                pos=(self.convention or self.expr).pos,
                arguments=[Asts.FunctionCallArgumentUnnamedAst(pos=self.expr.pos, convention=self.convention, value=self.expr)])
            ast.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        Check the memory integrity of the expression. This is a regular expression AST, so deeper analysis may be
        required.
        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        # Todo: memory checks involving "with"

        if self.expr and self.kw_with is None:
            ast = Asts.FunctionCallArgumentGroupAst(
                pos=(self.convention or self.expr).pos,
                arguments=[Asts.FunctionCallArgumentUnnamedAst(pos=self.expr.pos, convention=self.convention, value=self.expr)])
            ast.check_memory(sm, **kwargs)


__all__ = [
    "GenExpressionAst"]
