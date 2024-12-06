from unittest import TestCase

from tst._Utils import *


class TestParenthesizedExpressionAst(TestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_parenthesized_expression_invalid_expression_type(self):
        """
        fun f() -> std::Void {
            let a = (std::Bool)
        }
        """

    @should_pass_compilation()
    def test_valid_parenthesized_expression_valid_expression_type(self):
        """
        fun f() -> std::Void {
            let mut a = (true)
            a = false
        }
        """
