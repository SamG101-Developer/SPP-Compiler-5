from __future__ import annotations

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq

BINARY_METHODS = {
    SppTokenType.TkPlus: "add", SppTokenType.TkMinus: "sub", SppTokenType.TkMultiply: "mul", SppTokenType.TkDivide: "div",
    SppTokenType.TkRemainder: "rem", SppTokenType.TkModulo: "mod", SppTokenType.TkExponent: "pow", SppTokenType.KwAnd: "and_",
    SppTokenType.KwOr: "ior_", SppTokenType.TkEq: "eq", SppTokenType.TkNe: "ne", SppTokenType.TkLt: "lt",
    SppTokenType.TkGt: "gt", SppTokenType.TkLe: "le", SppTokenType.TkGe: "ge",
    SppTokenType.TkPlusAssign: "add_assign", SppTokenType.TkMinusAssign: "sub_assign",
    SppTokenType.TkMultiplyAssign: "mul_assign", SppTokenType.TkDivideAssign: "div_assign",
    SppTokenType.TkRemainderAssign: "rem_assign", SppTokenType.TkModuloAssign: "mod_assign",
    SppTokenType.TkExponentAssign: "pow_assign",
}

BINARY_OPERATOR_PRECEDENCE = {
    SppTokenType.KwOr: 1,
    SppTokenType.KwAnd: 2,
    SppTokenType.TkEq: 3,
    SppTokenType.TkNe: 3,
    SppTokenType.TkLt: 3,
    SppTokenType.TkGt: 4,
    SppTokenType.TkLe: 4,
    SppTokenType.TkGe: 4,
    SppTokenType.TkPlus: 5,
    SppTokenType.TkMinus: 5,
    SppTokenType.TkMultiply: 6,
    SppTokenType.TkDivide: 6,
    SppTokenType.TkRemainder: 6,
    SppTokenType.TkModulo: 6,
    SppTokenType.TkExponent: 6,
}

BINARY_COMPARISON_OPERATORS = {
    SppTokenType.TkEq, SppTokenType.TkNe, SppTokenType.TkLt, SppTokenType.TkGt, SppTokenType.TkLe, SppTokenType.TkGe,
}


class AstBinUtils:
    """!
    AstBinUtils contains a number of utility functions for working with binary expressions in the AST. There are
    functions to map binary expressions into postfix function calls (x + y => x.add(y)), to fix the associativity, and
    restructure comparison operators to support the Pythonic "0 < x < 1" syntax.
    """

    @staticmethod
    def convert_to_function_call(ast: Asts.BinaryExpressionAst) -> Asts.PostfixExpressionAst:
        ast = AstBinUtils._fix_associativity(ast)
        ast = AstBinUtils._combine_comparison_operators(ast)
        ast = AstBinUtils._convert_to_function_call(ast)
        return ast

    @staticmethod
    def _fix_associativity(ast: Asts.BinaryExpressionAst) -> Asts.BinaryExpressionAst:
        """
        The parser uses right-hand recursive parsing to mitigate left-hand-recursion in the binary operator parsing.
        This means the operators are in a reverse precedence order, and need to be re-arranged.
        """

        # If the rhs isn't a binary expression, then there is no handling needed.
        if not isinstance(ast.rhs, Asts.BinaryExpressionAst):
            return ast

        # If the ast precedence > the rhs operator's expression precedence, re-arrange the ast.
        elif BINARY_OPERATOR_PRECEDENCE[ast.op.token_type] >= BINARY_OPERATOR_PRECEDENCE[ast.rhs.op.token_type]:
            rhs = ast.rhs
            ast.rhs = rhs.rhs
            rhs.rhs = rhs.lhs
            rhs.lhs = ast.lhs
            rhs.op, ast.op = ast.op, rhs.op
            ast.lhs = rhs
            return AstBinUtils._fix_associativity(ast)

        # Otherwise, the ast is already in the correct order.
        else:
            return ast

    @staticmethod
    def _combine_comparison_operators(ast: Asts.BinaryExpressionAst) -> Asts.BinaryExpressionAst:
        """
        Expand chained comparison operators into their multiple parts. For example, the comparison "0 < a < 1" becomes
        "0 < a and a < 1".
        """

        # Check the lhs is a binary expression with a comparison operator.
        if not isinstance(ast.lhs, Asts.BinaryExpressionAst) or ast.op.token_type not in BINARY_COMPARISON_OPERATORS:
            return ast

        # Otherwise, split the lhs into two binary expressions recursively.
        else:
            lhs = ast.lhs.rhs
            rhs = ast.rhs
            ast.rhs = Asts.BinaryExpressionAst(ast.pos, lhs, ast.op, rhs)
            ast.op = Asts.TokenAst.raw(token_type=SppTokenType.KwAnd)
            AstBinUtils._combine_comparison_operators(ast)
            return ast

    @staticmethod
    def _convert_binary_expression_to_function_call(ast: Asts.BinaryExpressionAst) -> Asts.PostfixExpressionAst:
        method_name = BINARY_METHODS.get(ast.op.token_type, None)
        function_call_ast = CodeInjection.inject_code(
            f"{ast.lhs}.{method_name}()", SppParser.parse_postfix_expression, pos_adjust=ast.pos)
        function_call_ast.op.function_argument_group.arguments = Seq([Asts.FunctionCallArgumentUnnamedAst(value=ast.rhs)])
        return function_call_ast

    @staticmethod
    def _convert_is_expression_to_function_call(ast: Asts.IsExpressionAst) -> Asts.CaseExpressionAst:
        case_ast = CodeInjection.inject_code(
            f"case {ast.lhs} of is {ast.rhs} {{}}", SppParser.parse_case_expression, pos_adjust=ast.pos)
        return case_ast

    @staticmethod
    def _convert_to_function_call(ast: Asts.ExpressionAst) -> Asts.PostfixExpressionAst | Asts.BinaryExpressionAst:
        """
        Convert the binary expression into a postfix expression, with the binary operator being a function call.
        """

        # Nested parts of the binary expressions could be any expression.
        if not isinstance(ast, Asts.BinaryExpressionAst):
            return ast

        ast.lhs = AstBinUtils._convert_to_function_call(ast.lhs)
        ast.rhs = AstBinUtils._convert_to_function_call(ast.rhs)
        return AstBinUtils._convert_binary_expression_to_function_call(ast)


__all__ = ["AstBinUtils"]
