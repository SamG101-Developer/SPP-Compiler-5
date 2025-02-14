from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


@dataclass
class GenExpressionAst(Ast, TypeInferrable):
    tok_gen: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwGen))
    tok_with: Optional[Asts.TokenAst] = field(default=None)
    convention: Asts.ConventionAst = field(default=None)
    expression: Optional[Asts.ExpressionAst] = field(default=None)

    _func_ret_type: Optional[Asts.TypeAst] = field(default=None, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_gen.print(printer),
            self.tok_with.print(printer) if self.tok_with else "",
            self.convention.print(printer),
            self.expression.print(printer) if self.expression else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        # The inferred type of a gen expression is the type of the value being sent back into the coroutine.
        generator_type = self._func_ret_type
        send_type = generator_type.type_parts()[0].generic_argument_group["Send"].value
        return InferredTypeInfo(send_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Check the enclosing function is a coroutine and not a subroutine.
        if kwargs["function_type"].token.token_type != SppTokenType.KwCor:
            raise SemanticErrors.FunctionSubroutineContainsGenExpressionError().add(kwargs["function_type"], self.tok_gen)
        self._func_ret_type = kwargs["function_ret_type"]

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expression:
            self.expression.analyse_semantics(scope_manager, **kwargs)
            expression_type = self.expression.infer_type(scope_manager, **kwargs)
        else:
            void_type = CommonTypes.Void(self.pos)
            expression_type = void_type

        # Determine the yield's convention (based on convention token and symbol information)
        match self.convention, expression_type.convention:
            case Asts.ConventionMovAst(), symbol_convention: expression_type.convention = symbol_convention
            case _: expression_type.convention = self.convention

        # Determine the yield type of the enclosing function.
        external_gen_type = kwargs["function_ret_type"]
        internal_gen_type = external_gen_type.type_parts()[0].generic_argument_group["Gen"].value
        expected_type = InferredTypeInfo(internal_gen_type, CommonTypes.type_variant_to_convention(external_gen_type))

        # If the "with" keyword is being used, the expression type is the Gen generic type parameter.
        # Todo: this doesnt actually do anything?
        if self.tok_with:
            expression_type = InferredTypeInfo(internal_gen_type)

        # Check the expression type matches the expected type.
        if not expected_type.symbolic_eq(expression_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(internal_gen_type, expected_type, self.expression, expression_type)

        # Apply the function argument law of exclusivity checks to the expression.
        if self.expression:
            ast = AstMutation.inject_code(f"({self.convention} {self.expression})", SppParser.parse_function_call_arguments)
            ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenExpressionAst"]
