from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class GenExpressionAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_gen: TokenAst
    tok_with: Optional[TokenAst]
    convention: ConventionAst
    expression: Optional[ExpressionAst]
    _func_ret_type: Optional[TypeAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.ASTs.ConventionMovAst import ConventionMovAst

        # Create defaults.
        self.convention = self.convention or ConventionMovAst.default()

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_gen.print(printer),
            self.tok_with.print(printer) if self.tok_with else "",
            self.convention.print(printer),
            self.expression.print(printer) if self.expression else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # The inferred type of a gen expression is the type of the value being sent back into the coroutine.
        generator_type = self._func_ret_type
        send_type = generator_type.types[-1].generic_argument_group["Send"].value
        return InferredType.from_type(send_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import ConventionMovAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Check the enclosing function is a coroutine and not a subroutine.
        if kwargs["function_type"].token.token_type != TokenType.KwCor:
            raise AstErrors.GEN_OUTSIDE_COROUTINE(self.tok_gen, kwargs["function_type"])
        self._func_ret_type = kwargs["function_ret_type"]

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expression:
            self.expression.analyse_semantics(scope_manager, **kwargs)
            expression_type = self.expression.infer_type(scope_manager, **kwargs)
        else:
            void_type = CommonTypes.Void(self.pos)
            expression_type = InferredType.from_type(void_type)

        # Determine the yield's convention (based on convention token and symbol information)
        match self.convention, expression_type.convention:
            case ConventionMovAst(), symbol_convention: expression_type.convention = symbol_convention
            case _: expression_type.convention = self.convention

        # Determine the yield type of the enclosing function.
        expected_type = InferredType(
            convention=CommonTypes.type_variant_to_convention(kwargs["function_ret_type"]),
            type=kwargs["function_ret_type"].types[-1].generic_argument_group["Gen"].value)

        # Check the expression type matches the expected type.
        if not expected_type.symbolic_eq(expression_type, scope_manager.current_scope):
            raise AstErrors.TYPE_MISMATCH(expression_type.type, expected_type, self.expression, expected_type)

        # Apply the function argument law of exclusivity checks to the expression.
        ast = AstMutation.inject_code(f"({self.expression})", Parser.parse_function_call_arguments)
        ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenExpressionAst"]
