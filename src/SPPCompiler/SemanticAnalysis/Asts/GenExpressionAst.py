from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


@dataclass
class GenExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_gen: Asts.TokenAst = field(default=None)
    kw_with: Optional[Asts.TokenAst] = field(default=None)
    convention: Asts.ConventionAst = field(default=None)
    expression: Optional[Asts.ExpressionAst] = field(default=None)

    _func_ret_type: Optional[Asts.TypeAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_gen = self.kw_gen or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwGen)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_gen.print(printer),
            self.kw_with.print(printer) if self.kw_with else "",
            self.convention.print(printer),
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
        self._func_ret_type = kwargs["function_ret_type"]

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expression:
            self.expression.analyse_semantics(sm, **kwargs)
            expression_type = self.expression.infer_type(sm, **kwargs).with_convention(self.convention)
        else:
            void_type = CommonTypes.Void(self.pos)
            expression_type = void_type

        # Determine the yield type of the enclosing function.
        generator_type = kwargs["function_ret_type"]
        yield_type = generator_type.type_parts()[0].generic_argument_group["Yield"].value

        # Check the expression type matches the expected type.
        if not self.kw_with and not yield_type.symbolic_eq(expression_type, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(yield_type, yield_type, expression_type, expression_type).scopes(sm.current_scope)

        # If the "with" keyword is being used, the expression type must be a Gen type that matches the function_ret_type.
        if self.kw_with and not generator_type.symbolic_eq(expression_type, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(generator_type, generator_type, expression_type, self.expression).scopes(sm.current_scope)

        # Apply the function argument law of exclusivity checks to the expression.
        if self.expression:
            ast = CodeInjection.inject_code(
                f"({self.convention} {self.expression})", SppParser.parse_function_call_arguments,
                pos_adjust=self.convention.pos)
            ast.analyse_semantics(sm, **kwargs)


__all__ = [
    "GenExpressionAst"]
