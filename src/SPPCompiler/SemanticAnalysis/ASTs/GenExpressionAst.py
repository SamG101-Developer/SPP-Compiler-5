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
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


@dataclass
class GenExpressionAst(Ast, TypeInferrable):
    tok_gen: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwGen))
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

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # The inferred type of a gen expression is the type of the value being sent back into the coroutine.
        generator_type = self._func_ret_type
        send_type = generator_type.type_parts()[0].generic_argument_group["Send"].value
        return send_type

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Check the enclosing function is a coroutine and not a subroutine.
        if kwargs["function_type"].token_type != SppTokenType.KwCor:
            raise SemanticErrors.FunctionSubroutineContainsGenExpressionError().add(kwargs["function_type"], self.tok_gen)
        self._func_ret_type = kwargs["function_ret_type"]

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expression:
            self.expression.analyse_semantics(scope_manager, **kwargs)
            expression_type = self.expression.infer_type(scope_manager, **kwargs).with_convention(self.convention)
        else:
            void_type = CommonTypes.Void(self.pos)
            expression_type = void_type

        # Determine the yield type of the enclosing function.
        yield_type = kwargs["function_ret_type"].type_parts()[0].generic_argument_group["Yield"].value

        # If the "with" keyword is being used, the expression type is the Gen generic type parameter.
        if self.tok_with:
            expression_type = yield_type  # ?

        # Check the expression type matches the expected type.
        if not yield_type.symbolic_eq(expression_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(yield_type, yield_type, expression_type, expression_type)

        # Apply the function argument law of exclusivity checks to the expression.
        if self.expression:
            ast = AstMutation.inject_code(f"({self.convention} {self.expression})", SppParser.parse_function_call_arguments)
            ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenExpressionAst"]
