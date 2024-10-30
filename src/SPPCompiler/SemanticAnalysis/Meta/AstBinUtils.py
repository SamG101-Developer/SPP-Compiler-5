from typing import TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import TokenType

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.BinaryExpressionAst import BinaryExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionAst import PostfixExpressionAst


BINARY_METHODS = {
    TokenType.TkAdd: "add", TokenType.TkSub: "sub", TokenType.TkMul: "mul", TokenType.TkDiv: "div",
    TokenType.TkRem: "rem", TokenType.TkMod: "mod", TokenType.TkExp: "pow", TokenType.KwAnd: "and_",
    TokenType.KwOr: "ior_", TokenType.TkEq: "eq", TokenType.TkNe: "ne", TokenType.TkLt: "lt", TokenType.TkGt: "gt",
    TokenType.TkLe: "le", TokenType.TkGe: "ge", TokenType.TkSs: "cmp", TokenType.TkAddAssign: "add_assign",
    TokenType.TkSubAssign: "sub_assign", TokenType.TkMulAssign: "mul_assign", TokenType.TkDivAssign: "div_assign",
    TokenType.TkRemAssign: "rem_assign", TokenType.TkModAssign: "mod_assign", TokenType.TkExpAssign: "pow_assign",
}


BINARY_OPERATOR_PRECEDENCE = {
    TokenType.KwOr: 1,
    TokenType.KwAnd: 2,
    TokenType.TkEq: 3,
    TokenType.TkNe: 3,
    TokenType.TkLt: 3,
    TokenType.TkGt: 4,
    TokenType.TkLe: 4,
    TokenType.TkGe: 4,
    TokenType.TkSs: 4,
    TokenType.TkAdd: 5,
    TokenType.TkSub: 5,
    TokenType.TkMul: 6,
    TokenType.TkDiv: 6,
    TokenType.TkRem: 6,
    TokenType.TkMod: 6,
    TokenType.TkExp: 6,
}


BINARY_COMPARISON_OPERATORS = {
    TokenType.TkEq, TokenType.TkNe, TokenType.TkLt, TokenType.TkGt, TokenType.TkLe, TokenType.TkGe,
}


class AstBinUtils:
    @staticmethod
    def convert_to_function_call(ast: BinaryExpressionAst) -> PostfixExpressionAst:
        ast = AstBinUtils._fix_associativity(ast)
        ast = AstBinUtils._combine_comparison_operators(ast)
        ast = AstBinUtils._convert_to_function_call(ast)
        return ast

    @staticmethod
    def _fix_associativity(ast: BinaryExpressionAst) -> BinaryExpressionAst:
        """
        The parser uses right-hand recursive parsing to mitigate left-hand-recursion in the binary operator parsing.
        This means the operators are in a reverse precedence order, and need to be re-arranged.
        """

        # If the rhs isn't a binary expression, then there is no handling needed.
        if not isinstance(ast.rhs, BinaryExpressionAst):
            return ast

        # If the ast precedence > the rhs operator's expression precedence, re-arrange the ast.
        elif BINARY_OPERATOR_PRECEDENCE[ast.op.token.token_type] >= BINARY_OPERATOR_PRECEDENCE[ast.rhs.op.token.token_type]:
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
    def _combine_comparison_operators(ast: BinaryExpressionAst) -> BinaryExpressionAst:
        """
        Expand chained comparison operators into their multiple parts. For example, the comparison "0 < a < 1" becomes
        "0 < a and a < 1".
        """

        from SPPCompiler.SemanticAnalysis import BinaryExpressionAst, TokenAst

        # Check the lhs is a binary expression with a comparison operator.
        if not isinstance(ast.lhs, BinaryExpressionAst) or ast.op.token.token_type not in BINARY_COMPARISON_OPERATORS:
            return ast

        # Otherwise, split the lhs into two binary expressions recursively.
        else:
            lhs = ast.lhs.rhs
            rhs = ast.rhs
            ast.rhs = BinaryExpressionAst(ast.pos, lhs, ast.op, rhs)
            ast.op = TokenAst.default(TokenType.KwAnd)
            AstBinUtils._combine_comparison_operators(ast)
            return ast

    @staticmethod
    def _convert_to_function_call_inner(ast: BinaryExpressionAst) -> PostfixExpressionAst:
        """
        Convert the binary expression into a postfix expression, with the binary operator being a function call.
        """

        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Standard binary operators are converted into function calls.
        if method_name := BINARY_METHODS.get(ast.op.token.token_type, None):
            function_call_ast = AstMutation.inject_code(f"{ast.lhs}.{method_name}({ast.rhs})", Parser.parse_postfix_expression)
            return function_call_ast

        # Convert the "is" expression into a case-pattern block.
        elif ast.op.token.token_type == TokenType.KwIs:
            case_ast = AstMutation.inject_code(f"case {ast.lhs} then is {ast.rhs} {{}}", Parser.parse_case_expression)
            return case_ast

    @staticmethod
    def _convert_to_function_call(ast: BinaryExpressionAst) -> PostfixExpressionAst:
        """
        Convert the binary expression into a postfix expression, with the binary operator being a function call.
        """

        # Nested parts of the binary expressions could be any expression.
        if not isinstance(ast, BinaryExpressionAst):
            return ast

        ast.lhs = AstBinUtils._convert_to_function_call(ast.lhs)
        ast.rhs = AstBinUtils._convert_to_function_call(ast.rhs)
        return AstBinUtils._convert_to_function_call_inner(ast)


__all__ = ["AstBinUtils"]
