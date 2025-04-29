from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class GenExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_gen: Asts.TokenAst = field(default=None)
    kw_with: Optional[Asts.TokenAst] = field(default=None)
    convention: Optional[Asts.ConventionAst] = field(default=None)
    expression: Optional[Asts.ExpressionAst] = field(default=None)

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
            self.expression.print(printer) if self.expression else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.expression.pos_end if self.expression else self.kw_gen.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # The inferred type of a gen expression is the type of the value being sent back into the coroutine.
        generator_type = self._func_ret_type
        send_type = generator_type.type_parts()[0].generic_argument_group["Send"].value
        return send_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check the enclosing function is a coroutine and not a subroutine.
        if kwargs["function_type"].token_type != SppTokenType.KwCor:
            raise SemanticErrors.FunctionSubroutineContainsGenExpressionError().add(kwargs["function_type"], self.kw_gen).scopes(sm.current_scope)

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expression:
            self.expression.analyse_semantics(sm, **kwargs)
            expression_type = self.expression.infer_type(sm, **kwargs).with_convention(self.convention)
        else:
            void_type = CommonTypes.Void(self.pos)
            expression_type = void_type

        if kwargs["function_ret_type"]:
            self._func_ret_type = kwargs["function_ret_type"][0]
        else:
            # Todo: untested
            self._func_ret_type = CommonTypes.Gen(expression_type, CommonTypesPrecompiled.VOID)
            kwargs["function_ret_type"].append(self._func_ret_type)

        # Determine the yield type of the enclosing function.
        gen_type, yield_type = AstTypeUtils.get_generator_and_yielded_type(
            kwargs["function_ret_type"][0], sm, kwargs["function_ret_type"][0], "coroutine")

        # Check the expression type matches the expected type.
        if not self.kw_with and not yield_type.symbolic_eq(expression_type, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(yield_type, yield_type, expression_type, expression_type).scopes(sm.current_scope)

        # If the "with" keyword is being used, the expression type must be a Gen type that matches the function_ret_type.
        if self.kw_with and not kwargs["function_ret_type"][0].symbolic_eq(expression_type, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(kwargs["function_ret_type"][0], kwargs["function_ret_type"][0], self.expression, expression_type).scopes(sm.current_scope)

        # Apply the function argument law of exclusivity checks to the expression.
        if self.expression:
            ast = Asts.FunctionCallArgumentGroupAst(
                pos=(self.convention or self.expression).pos,
                arguments=[
                    Asts.FunctionCallArgumentUnnamedAst(
                        pos=self.expression.pos,
                        convention=self.convention,
                        value=self.expression
                    )
                ]
            )

            ast.analyse_semantics(sm, **kwargs)


__all__ = [
    "GenExpressionAst"]
